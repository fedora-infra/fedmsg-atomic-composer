import os
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
        self.watch_dir = self.config['watch_dir']
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
        # Create the directory ourselves so ostree will inherit our ownership
        repo_path = os.path.join(self.config['watch_dir'], repo)
        if not os.path.exists(repo_path):
            os.makedirs(os.path.join(self.config['watch_dir'], repo))

        task = os.path.join(self.config['touch_dir'], repo, 'treecompose')
        self.log.info('Touching %s', task)
        self.call(['touch', task])
        self.notifier.watch(filepath.FilePath(task),
                            callbacks=[self.output_changed])

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
        out = self.call(['rsync', '-ave', 'ssh',
            os.path.join(self.config['production_repos'], repo, 'repo'),
            os.path.join(self.config['local_repos'], repo, 'repo')])

    def sync_out(self, repo):
        """Sync the output to production"""
        self.call(['rsync', '-ave', 'ssh',
                   os.path.join(self.config['watch_dir'], repo, 'repo'),
                   os.path.join(self.config['production_repos'], repo, 'repo')])

    def output_changed(self, watch, path, mask):
        """Called when something in the output directory changes.

        If we've never seen the 
        """
        self.log.info('%s %s', inotify.humanReadableMask(mask), path)
        if not path.exists():
            self.log.info('%s complete!', path)
            self.notifier.ignore(path)
            repo = path.dirname().split('/')[-1]
            self.update_ostree_summary(repo)
        else:
            self.log.info('%s already exists, and was modified?', path)

    def update_ostree_summary(self, repo):
        self.log.info('Updating the ostree summary for %s', repo)
        repo_path = os.path.join(self.config['watch_dir'], repo, 'repo')
        self.call(['ostree', '--repo=' + repo_path, 'summary', '--update'])
