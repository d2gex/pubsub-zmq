import zmq
import json

from pubsub_zmq import ipeer


class PubPeer(ipeer.IPeer):
    '''This class is not usually instantiated and only extended by Sub-type ends
    '''

    def __init__(self, *args, timeout=1, num_attempts=5, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout = timeout
        self.num_attempts = num_attempts
        self.sndhwm = kwargs.get('sndhwm', 1000)  # 1000 is the default value according to Zeromq
        self.socket_type = zmq.PUB
        self.socket = self.context.socket(self.socket_type)
        self.socket.setsockopt(zmq.LINGER, self.linger)
        self.socket.setsockopt(zmq.SNDHWM, self.sndhwm)

    def run(self, topic, data, encoding='utf-8'):
        '''It sends a message downstream as many times as subscribers are subscribed to the topic of such message. No
        retries as pub will just drop messages if the other side isn't available
        '''
        self.socket.send_multipart([json.dumps(topic).encode(encoding),
                                    json.dumps(data).encode(encoding)])
