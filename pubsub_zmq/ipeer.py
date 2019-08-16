import abc

MAX_IPC_URL_LENGTH = 133


class IPeer(abc.ABC):
    '''Class Interface from which the different Push/Pull end peers will need to extend. It provides a common structure
    and clutter common code around its constructor
    '''

    def __init__(self, url, identity, **kwargs):
        if 'ipc://' in url and len(url) > MAX_IPC_URL_LENGTH:
            raise ValueError(f"IPC URL '{url}' cannot have more than {MAX_IPC_URL_LENGTH} characters long")
        self.url = url
        self.identity = identity
        self.linger = kwargs.get('linger', 0)
        self.timeout = None
        self.socket = None
        self.socket_type = None
        self.context = None

    @abc.abstractmethod
    def run(self, *args, **kwargs):
        pass

    def clean(self):
        if not self.socket.closed:
            self.socket.close()
        if not self.context.closed:
            self.context.term()
