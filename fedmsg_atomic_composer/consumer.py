# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import fedmsg.consumers

from twisted.internet import reactor

from .composer import AtomicComposer


class AtomicConsumer(fedmsg.consumers.FedmsgConsumer):
    """A fedmsg-driven atomic ostree composer.

    This consumer runs in the fedmsg-hub and reacts to whenever repositories
    sync to the master mirror.
    """
    def __init__(self, hub, *args, **kw):
        # Map all of the options from our /etc/fedmsg.d config to self
        for key, item in hub.config.items():
            setattr(self, key, item)

        self.topic = getattr(self, 'fedmsg_atomic_topic', None)

        super(AtomicConsumer, self).__init__(hub, *args, **kw)

        if not self.topic:
            self.log.warn("No 'fedmsg_atomic_topic' set.")

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
            self.log.info('New Fedora %(release)s %(repo)s compose ready',
                          body['msg'])
            repo = 'f%(release)s-%(repo)s' % body['msg']
        else:
            self.log.warn('Unknown topic: %s', topic)

        release = self.releases[repo]
        reactor.callInThread(self.compose, release)

    def compose(self, release):
        self.composer = AtomicComposer()
        result = self.composer.compose(release)
        if result['result'] == 'success':
            self.log.info(result)
        else:
            self.log.error(result)
