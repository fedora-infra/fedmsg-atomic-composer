import os
import json
import shutil
import librepo
import iniparse
import subprocess
import fedmsg.consumers

from twisted.internet import inotify
from twisted.python import filepath


class AtomicComposer(fedmsg.consumers.FedmsgConsumer):
    config_key = 'fedmsg_atomic_composer'

    def __init__(self, hub, *args, **kw):
        self.config = hub.config
        self.topic = self.config['topic']
        super(AtomicComposer, self).__init__(hub, *args, **kw)
        self.output_dir = self.config['output_dir']
        self.notifier = inotify.INotify()
        self.notifier.startReading()

    def consume(self, msg):
        self.log.debug(msg)
        body = msg['body']
        topic = body['topic']
        repo = None

        if 'rawhide' in topic:
            arch = body['msg']['arch']
            self.log.info('New rawhide %s compose ready', arch)
            repo = 'rawhide'
        elif 'branched' in topic:
            arch = body['msg']['arch']
            branch = body['msg']['branch']
            self.log.info('New %s %s branched compose ready', branch, arch)
            log = body['msg']['log']
            if log != 'done':
                self.log.warn('Compose not done?')
                return
            repo = branch
        elif 'updates.fedora' in topic:
            self.log.info('New %(release)s %(repo)s compose ready', body['msg'])
            repo = 'f' + body['msg']['release']
        else:
            self.log.warn('Unknown topic: %s', topic)

        self.sync_in(repo)
        self.trigger_compose(repo)

    def trigger_compose(self, repo):
        """Trigger the rpm-ostree-toolbox taskrunner treecompose"""
        task = os.path.join(self.config['touch_dir'], repo, 'treecompose')
        self.log.info('Touching %s', task)
        self.call(['touch', task])
        self.notifier.watch(filepath.FilePath(task),
                            callbacks=[self.compose_complete])

    def call(self, cmd, **kwargs):
        self.log.info('Running %s', cmd)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, **kwargs)
        out, err = p.communicate()
        if err:
            self.log.error(err)
        return out, err, p.returncode

    def sync_in(self, repo):
        """Sync the canonical ostree locally"""
        out, err, returncode = self.call(['rsync', '-ave', 'ssh',
            os.path.join(self.config['production_repos'], repo),
            os.path.join(self.config['output_dir'])])
        self.log.info(out)

    def sync_out(self, repo):
        """Sync the output to production"""
        out, err, returncode = self.call(['rsync', '-ave', 'ssh', repo,
                                         self.config['production_repos']],
                                         cwd=self.config['output_dir'])
        self.log.info(out)

    def compose_complete(self, watch, path, mask):
        """Called when our tree compose has completed"""
        self.log.info('%s %s', inotify.humanReadableMask(mask), path)
        if not path.exists():
            self.log.info('%s complete!', path)
            self.notifier.ignore(path)
            repo = path.dirname().split('/')[-1]
            self.update_ostree_summary(repo)
            config = self.parse_config(repo)
            self.download_repodata(repo, config)
            self.sync_out(repo)
        else:
            self.log.info('%s already exists, and was modified?', path)

    def update_ostree_summary(self, repo):
        self.log.info('Updating the ostree summary for %s', repo)
        repo_path = os.path.join(self.config['output_dir'], repo, 'repo')
        self.call(['ostree', '--repo=' + repo_path, 'summary', '--update'])

    def extract_treefile(self, repo, config):
        """Extract and decode the treefile JSON from the composed tree"""
        ref = config.get('DEFAULT', 'ref')
        repo_path = os.path.join(self.config['output_dir'], repo, 'repo')
        out, err, code = self.call(['ostree', '--repo=' + repo_path, 'cat', ref,
                                    '/usr/share/rpm-ostree/treefile.json'])
        if err:
            self.log.error(err)
        if code != 0:
            self.log.error(out)
            return
        return json.loads(out)

    def parse_config(self, repo):
        """Parse the config.ini for a given repo"""
        config = iniparse.ConfigParser()
        config.read(os.path.join(self.config['local_repos'], repo, 'config.ini'))
        return config

    def download_repodata(self, repo, config):
        """
        Determine the repositories used to compose this tree, and sync the
        repodata locally. We do this by extracting the JSON treefile from the
        composed ostree, and for each repo listed parsing the URL from the
        fedora-atomic.git/$REPO.repo file.
        """
        arch = config.get('DEFAULT', 'arch')
        treefile = self.extract_treefile(repo, config)
        for yum_repo in treefile['repos']:
            handle = librepo.Handle()
            handle.repotype = librepo.LR_YUMREPO

            repo_file = os.path.join(self.config['local_repos'], repo,
                                     'fedora-atomic', yum_repo + '.repo')
            if os.path.exists(repo_file):
                self.log.info('Found yum repo: %s', repo_file)
                config = iniparse.ConfigParser()
                config.read(repo_file)
                try:
                    url = config.get(yum_repo, 'baseurl')
                    url = url.replace('$basearch', arch)
                    handle.urls = [url]
                except iniparse.NoOptionError:
                    url = config.get(yum_repo, 'mirrorlist')
                    url = url.replace('$basearch', arch)
                    handle.mirrorlist = url

                dest = os.path.join(self.config['output_dir'], repo,
                                    yum_repo + '.repodata')
                if os.path.exists(dest):
                    shutil.rmtree(dest)
                os.mkdir(dest)
                handle.destdir = dest

                result = librepo.Result()
                try:
                    self.log.info('Downloading repo metadata from %s', url)
                    handle.perform(result)
                    self.log.info('Repo metadata saved to %s', dest)
                except:
                    self.log.exception('Unable to download repodata')
            else:
                self.log.error('Unable to find repo: %s', repo_file)
