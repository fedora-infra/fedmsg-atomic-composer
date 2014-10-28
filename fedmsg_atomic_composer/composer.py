import os
import glob
import json
import shutil
import librepo
import iniparse
import subprocess
import fedmsg.consumers

from zope.interface import implements

from twisted.internet.interfaces import IReadDescriptor
from twisted.internet import inotify
from twisted.python import filepath

from twisted.internet import reactor

from systemd import journal


class AtomicComposer(fedmsg.consumers.FedmsgConsumer):
    """A fedmsg-driven atomic ostree composer.

    This consumer runs in the fedmsg-hub and reacts to whenever repositories
    sync to the master mirror. When this happens we trigger the
    rpm-ostree-toolbox taskrunner to kick off a treecompose by touching a file
    under the `touch_dir`. We then monitor the output of the compose using the
    systemd journal and upon completion perform various post-compose actions.
    """
    implements(IReadDescriptor)

    def __init__(self, hub, *args, **kw):
        # Map all of the options from our /etc/fedmsg.d config to self
        for key, item in hub.config.items():
            setattr(self, key, item)

        # Monitor the output of our taskrunner services
        self.journal = journal.Reader()
        for tree in self.trees:
            self.journal.add_match(_SYSTEMD_UNIT='atomic-compose-%s.service' % tree)
        self.journal.seek_tail()
        self.journal.get_previous()
        reactor.addReader(self)

        super(AtomicComposer, self).__init__(hub, *args, **kw)

    def consume(self, msg):
        """Called with each incoming fedmsg.

        From here we trigger an rpm-ostree compose by touching a specific file
        under the `touch_dir`. Then our `doRead` method is called with the
        output of the rpm-ostree-toolbox treecompose, which we monitor to
        determine when it has completed.
        """
        self.log.info(msg)
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

        if not os.path.isdir(os.path.join(self.touch_dir, repo)):
            self.log.info('Skipping %s', repo)
            return

        self.sync_in(repo)
        self.trigger_compose(repo)

    def trigger_compose(self, repo):
        """Trigger the rpm-ostree-toolbox taskrunner treecompose"""
        task = os.path.join(self.touch_dir, repo, 'treecompose')
        self.log.info('Touching %s', task)
        self.call(['touch', task])

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
        prod = os.path.join(self.production_repos, repo)
        if os.path.exists(prod):
            out, err, returncode = self.call(['rsync', '-ave', 'ssh', prod,
                                              os.path.join(self.output_dir)])
            self.log.info(out)
        else:
            self.log.info('Production repo doesn\'t exist yet: %s', prod)

    def sync_out(self, repo):
        """Sync the output to production"""
        out, err, returncode = self.call(['rsync', '-ave', 'ssh', repo,
                                         self.production_repos],
                                         cwd=self.output_dir)
        self.log.info(out)

    def compose_complete(self, repo):
        """Called when our tree compose has completed"""
        self.log.info('%s complete!', repo)
        summary = self.update_ostree_summary(repo)
        #config = self.parse_config(repo)
        self.inject_summary_into_repodata(summary, repo)
        self.sync_out(repo)

    def update_ostree_summary(self, repo):
        """Update the ostree summary file and return a path to it"""
        self.log.info('Updating the ostree summary for %s', repo)
        repo_path = os.path.join(self.output_dir, repo, 'repo')
        self.call(['ostree', '--repo=' + repo_path, 'summary', '--update'])
        return os.path.join(repo_path, 'summary')

    def extract_treefile(self, repo, config):
        """Extract and decode the treefile JSON from the composed tree"""
        ref = config.get('DEFAULT', 'ref')
        repo_path = os.path.join(self.output_dir, repo, 'repo')
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
        config.read(os.path.join(self.local_repos, repo, 'config.ini'))
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

            repo_file = os.path.join(self.local_repos, repo,
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

                dest = os.path.join(self.output_dir, repo,
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
                    self.log.info(result)
                    return dest
                except:
                    self.log.exception('Unable to download repodata')
            else:
                self.log.error('Unable to find repo: %s', repo_file)

    def inject_summary_into_repodata(self, summary, repo):
        """Inject the ostree summary file into the yum repodata"""
        self.log.info('Injecting ostree summary into yum repodata')
        repomd = glob.glob(os.path.join(self.output_dir, repo, 'repodata',
                                        '*', 'repomd.xml'))
        for md in repomd:
            self.log.info('Found repodata: %s', md)
            #repodata = os.path.dirname(md)
            #os.unlink(md)
            #os.symlink(summary, md)
            #self.log.info('%s -> %s symlink created', summary, md)

    def fileno(self):
        """Returns our systemd journal descriptor to Twisted"""
        return self.journal.fileno()

    def logPrefix(self):
        """Needed for Twisted's IReadDescriptor interface"""
        return self.__class__.__name__

    def connectionLost(self, reason):
        self.log.error('connection lost: %s', reason)
        reactor.removeReader(self)
        self.journal.close()
        raise reason

    def doRead(self):
        """Called when data is available from the journal"""
        if self.journal.process() != journal.APPEND:
            return
        for entry in self.journal:
            if entry['MESSAGE'] == 'INFO:root:task treecompose exited successfully':
                unit = entry['_SYSTEMD_UNIT']
                repo = unit.replace('atomic-compose-', '').replace('.service', '')
                reactor.callInThread(self.compose_complete, repo)
