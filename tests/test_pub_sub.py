import pytest
import multiprocessing
import time

from pymulproc import factory, mpq_protocol
from pubsub_zmq import ipeer, publisher
from tests import utils as test_utils, stubs


def call_publisher(cls, url, peer_name, comm, loops):
    '''Call a pub-like stub
    '''
    s = cls(identity=peer_name, url=url)
    s.mock(comm, loops=loops)


def call_subscriber(cls, topics, url, peer_name, comm, parent_pid):
    '''Call a sub-like stub
    '''
    s = cls(topics=topics, identity=peer_name, url=url, parent_pid=parent_pid)
    s.mock(comm, parent_pid=parent_pid)


class TestPublisherSubscriber:
    '''This class tests that the exchange between Publishers and Subscriber is done on the term of the PUB/SUB
    specification. The main strategy is that information is sent via PUB/SUB sockets and receive either via IPC
    communication using Python native Multiprocessing library - both PIPES and Queues.

    1. The socket exchange data structure is data = [topic, info]
    2. The IPC exchange [mpq_protocol.Operation, [topic, info]]
    '''

    @staticmethod
    def publisher_subscriber_one_to_one(topics, info):

        pipe_factory = factory.PipeCommunication()
        parent_comm = pipe_factory.parent()
        child_com = pipe_factory.child()
        subscriber_process = multiprocessing.Process(target=call_subscriber,
                                                     args=(stubs.SubscriberOKStub,
                                                           topics,
                                                           test_utils.TCP_CONNECT_URL_SOCKET,
                                                           "SubscriberOK",
                                                           child_com,
                                                           100))

        pub = publisher.Publisher(url=test_utils.TCP_BIND_URL_SOCKET, identity='PublisherOK', linger=0)
        messages = {}
        try:
            subscriber_process.start()

            # (1) Send message(s)
            time.sleep(0.1)  # wait a bit as messages sent by the publisher when subscriber is offline are lost forever
            sending_topics = [topics] if isinstance(topics, str) else topics
            for topic in sending_topics:
                pub.run(topic, info)

            # (2) Wait for the message(s) sent to the SubscriberOK peer, which will be sent back to us by using the
            # Multiprocessing PIPE channel
            stop = False
            loops = 10
            num_sms = 0
            while not stop:
                time.sleep(0.1)
                loops -= 1
                if loops <= 0:
                    stop = True
                else:
                    server_message = parent_comm.receive()
                    if server_message:
                        _topic, _info = server_message[-1]
                        messages[_topic] = _info
                        num_sms += 1
                        if num_sms == len(sending_topics):
                            stop = True

            # (3) Ensure the loop was finish because we did receive the message(s) we sent
            assert stop and loops > 0
        except KeyboardInterrupt:
            pass
        finally:
            subscriber_process.join()
            pub.clean()
        return messages

    def test_ipc_url_max_length(self):

        with pytest.raises(ValueError):
            publisher.Publisher(url=f"ipc://{'a' * (ipeer.MAX_IPC_URL_LENGTH + 1)}", identity='url_too_long')

    def test_publisher_subscriber_one_topic(self):
        ''' A publisher sends a single dictionary to a subscriber who is subscribed to only one topic. Therefore only
        one message is received.
        '''

        info = {'data': 'Info from publisher'}
        topic = 'A'
        messages = self.publisher_subscriber_one_to_one(topics=topic, info=info)
        assert len(messages) == 1
        assert topic in messages
        assert messages[topic] == info

    def test_publisher_subscriber_many_topic(self):
        ''' A publisher sends a single dictionary to a subscriber who is subscribed to various topics. Therefore one
        message per topic should be received
        '''

        info = {'data': 'Info from publisher'}
        topics = ['A', 'B', 'C']
        messages = self.publisher_subscriber_one_to_one(topics=topics, info=info)
        assert len(messages) == 3
        for topic in topics:
            assert messages[topic] == info

    def test_multiple_subscriber_one_publisher(self):
        '''Test that multiple simultaneous pushes can be handled by a sink. It also tests a practical case
        of Multiprocessing queue communication.

        It creates 5 child producers that will be sending data to the sink as a PUSH-ends. Then the same producers too
        send the same data but now via Multiprocessing queues. At the end we compare that the two data received are
        exactly the same to assert that the sink can handle multiple connections.
        '''

        queue_factory = factory.QueueCommunication()
        parent_comm = queue_factory.parent(timeout=0.1)

        # Create
        subscribers = []
        topics = ['A', 'B', 'C', 'D', 'E']
        info = {}
        for offset in range(5):
            subscribers.append(multiprocessing.Process(target=call_subscriber,
                                                       args=(stubs.SubscriberOKStub,
                                                             topics[offset],
                                                             test_utils.TCP_BIND_URL_SOCKET,
                                                             f"Subscriber_{offset}",
                                                             queue_factory.child(),
                                                             100)))
            info[topics[offset]] = f"data for topic {topics[offset]}"

        pub = publisher.Publisher(url=test_utils.TCP_BIND_URL_SOCKET, identity='Publisher', linger=0)
        try:
            for client in subscribers:
                client.start()

            # (1) Let's wait a bit for all subscriber to initialise before the publisher start sending info
            time.sleep(0.5)
            for offset in range(len(subscribers)):
                pub.run(topics[offset], info[topics[offset]])

            # (2) Wait for children processes to finish
            for client in subscribers:
                client.join()

            # (3) Now we know all data sent by the publisher needs to be received from subscriber via a shared queue
            results = []
            for _ in range(len(subscribers)):
                results.append(parent_comm.receive(func=lambda x: True)[-1])

            # (4) The queue should now be empty and all tasks done
            assert parent_comm.conn.empty()
            parent_comm.conn.join()

            # (5) Check they are the same elements
            assert len(results) == len(topics)
            for result in results:
                _topic, data = result
                assert _topic in topics
                assert info[_topic] == data

        except KeyboardInterrupt:
            pass
        finally:
            for client in subscribers:
                client.join()
            parent_comm.conn.join()
            pub.clean()
