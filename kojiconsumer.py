# An example fedmsg koji consumer

import fedmsg.consumers

from pprint import pprint

class KojiConsumer(fedmsg.consumers.FedmsgConsumer):
    topic = 'org.fedoraproject.prod.buildsys.*'
    config_key = 'kojiconsumer'

    def __init__(self, *args, **kw):
        super(KojiConsumer, self).__init__(*args, **kw)

    def consume(self, msg):
        pprint(msg)
