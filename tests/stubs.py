import abc

from pymulproc import mpq_protocol
from pubsub_zmq import subscriber


class StubBase:
    @abc.abstractmethod
    def mock(self, process_comm, **kwargs):
        '''Method that needs to be implemented in the subclasses and that will be used to generate the test cases of
        this peer side.
        '''
        pass


class SubscriberOKStub(StubBase, subscriber.Subscriber):

    def mock(self, process_comm, **kwargs):
        '''It will fetch data sent from the client via a SUB socket and return it back to the client by using a
        Multiprocessing PIPE, and so on and so forth until runs out of loops.
        '''

        try:
            # Polling for about 1s = 100 * 10ms(POLLING_TIMEOUT)
            loops = kwargs.get('loops', 100)
            while loops:
                loops -= 1
                client_data = self.run()
                if client_data:
                    # Any topic received we are not subscribed? => This is wrong
                    assert client_data[0] in self.topics if isinstance(self.topics, list) else [self.topics]
                    process_comm.send(mpq_protocol.REQ_FINISHED, data=client_data)
            assert not loops
        except KeyboardInterrupt:
            pass
            # ... close both the socket and context
        finally:
            self.clean()
