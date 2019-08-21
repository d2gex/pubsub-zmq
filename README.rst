===================================================================================
``PubSub-ZMQ``: A tiny library for PUB-SUB asynchronous communication
===================================================================================

A small library that abstracts the PUB-SUB asynchronous communication pattern by using PUB and SUB socket types
from ZeroMQ.

.. image:: https://travis-ci.com/d2gex/pubsub-zmq.svg?branch=master
    :target: https://github.com/d2gex/pubsub-zmq

.. image:: https://img.shields.io/badge/coverage-100%25-brightgreen.svg
    :target: #

The filtering of the messages occurs at 'Publisher' side, with subscribers receiving those messages which topics
they are subscribed to **only**. Both publishers and subscribers can be started in any other but any message that
publishers sent while subscribers are still offline, will be lost permanently. This is because publishers follows
a **"fire and forget"** strategy.

Install and Run
===============
Pubsub-ZMQ is not available on PyPI yet, so you need to install it with pip providing a GitHub path as
follows::

    $ pip install git+https://github.com/d2gex/pubsub-zmq.git@0.1.1#egg=pubsub-zmq


.. code-block:: python

    ''' A publisher that sends a sequence of numbers in descending order starting at 10  and finishing at 1'''

    publisher = publisher.Publisher(url=tcp://127.0.0.1:5556, identity='Publisher Name')
    loops = 10
    topic = 'descending_sequence'
    while loops:
        publisher.run(topic, loops)
        loops -= 1

where:

1.  **url**: Follows a format  `protocol://ip:port`. TCP, IPC and INPROC protocols are supported


.. code-block:: python

    ''' A subscriber that receives a sequence of numbers in descending order starting at 10 and finishing at 1'''

    subscriber = subscriber.Subscriber(topics=['descending_sequence'], url=tcp://127.0.0.1:5556, identity='Subscriber Name')
    loops = 10
    while loops:
        data = subscriber.run()
        print(data)
        loops -= 1

where:

1.  **topics**: is a list of topics to which the Subscriber is subscribed.