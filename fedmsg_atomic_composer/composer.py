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
        self.notifier.watch(filepath.FilePath(self.config['watch_dir']),
                            callbacks=[self.output_changed])

    def consume(self, msg):
        self.log.debug(msg)
        body = msg['body']
        topic = body['topic']

        if 'rawhide' in topic:
            arch = body['msg']['arch']
            self.log.info('New rawhide %s compose ready', arch)
            self.trigger_compose('rawhide')
        elif 'branched' in topic:
            arch = body['msg']['arch']
            branch = body['msg']['branch']
            self.log.info('New %s %s branched compose ready', branch, arch)
            log = body['msg']['log']
            if log != 'done':
                self.log.warn('Compose not done?')
                return
            self.trigger_compose(branch)
        elif 'updates' in topic:
            release = body['msg']['release']
            repo = body['msg']['repo']
            self.log.info('New %s %s compose ready', release, repo)
            self.trigger_compose(release)

    def trigger_compose(self, repo):
        """Trigger the rpm-ostree-toolbox taskrunner treecompose"""
        self.call(['touch', os.path.join(self.config['touch_dir'],
                   repo, 'treecompose')])

    def call(self, cmd, **kwargs):
        self.log.info('Running %s', cmd)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, **kwargs)
        out, err = p.communicate()
        return out, err, p.returncode

    def output_changed(self, watch, path, mask):
        self.log.info('Directory modified: %s', path)

        # extract summary
        # inject summary into repodata

        #if path.endswith('updates-testing'):
        #elif path.endswith('rawhide'):
        #elif path.endswith('branched'):
        #else:
