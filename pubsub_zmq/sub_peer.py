import zmq
import json

from pubsub_zmq import ipeer


class SubPeer(ipeer.IPeer):
    '''This class is not usually instantiated and only extended by Sub-type ends
    '''

    def __init__(self, topics, timeout=10, context=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout = timeout
        self.topics = topics
        self.socket_type = zmq.SUB
        self.context = context or zmq.Context()
        self.socket = self.context.socket(self.socket_type)
        self.socket.setsockopt(zmq.LINGER, self.linger)
        for topic in self.topics if isinstance(self.topics, list) else [self.topics]:
            self.socket.setsockopt_string(zmq.SUBSCRIBE, json.dumps(topic))
        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)

    def receive(self):
        '''Read the underlying socket and decode the received multiple frames from bytes to string and them to json
        '''
        return [json.loads(frame.decode()) for frame in self.socket.recv_multipart()]

    def run(self):
        '''Polls the socket in order to know if there is anything available to pick
        '''
        poll = dict(self.poller.poll(self.timeout))
        any_receivable = poll.get(self.socket, None)
        if any_receivable:
            return self.receive()
        return False
