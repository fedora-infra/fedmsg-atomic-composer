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

import copy
import tempfile
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
            self.log.info('New Fedora %(release)s %(repo)s compose ready',
                          body['msg'])
            repo = 'f%(release)s-%(repo)s' % body['msg']
        else:
            self.log.warn('Unknown topic: %s', topic)

        # Copy of the release dict and expand some paths
        release = copy.deepcopy(self.releases[repo])
        release['tmp_dir'] = tempfile.mkdtemp()
        for key in ('output_dir', 'log_dir'):
            release[key] = getattr(self, key).format(**release)

        composer = AtomicComposer()
        reactor.callInThread(composer.compose, release)
