from pubsub_zmq.pub_peer import PubPeer


class Publisher(PubPeer):
    '''Publisher end that will bind and send messages to subscribers
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.socket.bind(self.url)
