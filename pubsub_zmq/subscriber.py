from pubsub_zmq.sub_peer import SubPeer


class Subscriber(SubPeer):
    '''Subscriber end that will connect to the bound Publisher
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.socket.connect(self.url)
