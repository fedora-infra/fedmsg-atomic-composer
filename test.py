#!/usr/bin/env python
import os
import mock
import shutil
import unittest
import tempfile

from fedmsg_atomic_composer import AtomicComposer

class FakeHub(object):
    def __init__(self):
        self.config = {
            'config_key': 'fedmsg_atomic_composer',
            'topic_prefix': 'org.fedoraproject',
            'environment': 'dev',
            'releng_fedmsg_certname': None,
            'touch_dir': tempfile.mkdtemp(),
            'output_dir': tempfile.mkdtemp(),
            'production_repos': tempfile.mkdtemp(),
            'local_repos': tempfile.mkdtemp(),
            'topic': ['org.fedoraproject.test'],
            'trees': ['rawhide'],
        }

    def subscribe(self, *args, **kw):
        pass

updates_msg = {
    "body": {
        "i": 1,
        "msg": {
            "bytes": "352.15M",
            "deleted": "470",
            "release": "19",
            "repo": "updates"
        },
        "msg_id": "2014-74193fa4-bed3-40c3-9a0e-db2bcedf41ba",
        "timestamp": 1413724658.0,
        "topic": "org.fedoraproject.prod.bodhi.updates.fedora.sync"
    }
}


class TestAtomicComposer(unittest.TestCase):

    def setUp(self):
        self.composer = AtomicComposer(FakeHub())

    def tearDown(self):
        pass

    @mock.patch('fedmsg_atomic_composer.AtomicComposer.sync_in')
    @mock.patch('fedmsg_atomic_composer.AtomicComposer.sync_out')
    @mock.patch('fedmsg_atomic_composer.AtomicComposer.compose_complete')
    def test_updates(self, *args):
        fakehub = FakeHub()
        touch_dir = fakehub.config['touch_dir']
        os.makedirs(os.path.join(touch_dir, 'f19'))
        self.masher = AtomicComposer(fakehub)
        self.masher.consume(updates_msg)
        #call.assert_called_with(['touch', os.path.join(fakehub.config['touch_dir'],
        #                         '19', 'treecompose')])
        shutil.rmtree(fakehub.config['touch_dir'])
        shutil.rmtree(fakehub.config['output_dir'])
        shutil.rmtree(fakehub.config['production_repos'])
        shutil.rmtree(fakehub.config['local_repos'])


if __name__ == '__main__':
    unittest.main()
