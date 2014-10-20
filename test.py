#!/usr/bin/env python
import mock
import unittest

from ostreecomposer import OSTreeComposer

class FakeHub(object):
    def __init__(self):
        self.config = {
            'topic_prefix': 'org.fedoraproject',
            'environment': 'dev',
            'releng_fedmsg_certname': None,
            'touch_file': '/tmp/treecompose',
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


class TestOSTreeComposer(unittest.TestCase):

    def setUp(self):
        self.composer = OSTreeComposer(FakeHub())

    def tearDown(self):
        pass

    @mock.patch('ostreecomposer.OSTreeComposer.call')
    def test_updates(self, call):
        fakehub = FakeHub()
        self.masher = OSTreeComposer(fakehub)
        self.masher.consume(updates_msg)
        call.assert_called_with(['touch', fakehub.config['touch_file']])


if __name__ == '__main__':
    unittest.main()
