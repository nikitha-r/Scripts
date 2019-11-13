base-rabbitmq
app.py
-----

# Code for actually processing a rabbitMQ message
def on_rabbitmq_message(publisher, body, msg_properties):
    raise Exception("Your docker build file should overwrite app.py")

def on_rabbitmq_connected(consumer):
    """
    Callback method triggered when the rabbitmq client is successfully
    connected and the queue has been setup and bound

    Provides access to the Pika client. Should be overridden by implementing
    microservices if it is needed
    """
    pass
    
Rabbit.py
--------
# -*- coding: utf-8 -*-

import logging
import pika
import os
import ssl
import traceback
from functools import partial
from threading import Timer
import threading
import signal
import subprocess
import json

LOGGER = logging.getLogger(__name__)
process_lock = threading.Lock()

class RabbitMQConsumer(object):
    """This is an example consumer that will handle unexpected interactions
    with RabbitMQ such as channel and connection closures.

    If RabbitMQ closes the connection, it will reopen it. You should
    look at the output, as there are limited reasons why the connection may
    be closed, which usually are tied to permission related issues or
    socket timeouts.

    If the channel is closed, it will indicate a problem with one of the
    commands that were issued and that should surface in the output as well.

    """
    EXCHANGES = os.getenv('RABBIT_EXCHANGES', '').strip().split(',')
    ROUTING_KEY = os.getenv('RABBIT_ROUTING_KEY', '')
    EXCHANGE_TYPE = 'topic'
    QUEUE = os.getenv('RABBIT_QUEUE', 'python.messages')
    RABBIT_SERVER_CERT = os.environ.get('RABBIT_SERVER_CERT')
    RABBIT_CLIENT_KEY = os.environ.get('RABBIT_CLIENT_KEY')
    RABBIT_CLIENT_CERT = os.environ.get('RABBIT_CLIENT_CERT')
    RABBIT_PREFETCH = int(os.getenv('RABBIT_PREFETCH', 1))
    RABBIT_MESSAGE_HANDLER_TIMEOUT = int(os.getenv('RABBIT_MESSAGE_HANDLER_TIMEOUT', 60))

    def __init__(self, amqp_url, on_message = None, options = {}):
        """Create a new instance of the consumer class, passing in the AMQP
        URL used to connect to RabbitMQ.

        :param str amqp_url: The AMQP url to connect with

        """
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._url = amqp_url
        self.on_message_handler = on_message
        self.isQueueEstablished = False
        self.isConsuming = False
        self.options = options
        self.basic_consume_args = None
        self.on_connected_handler = None

        if 'basic_consume_args' in options:
            self.basic_consume_args = options['basic_consume_args']
        if 'on_connected' in options:
            self.on_connected_handler = options['on_connected']

    def connect(self):
        """This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika.

        :rtype: pika.SelectConnection

        """
        LOGGER.info('Connecting to %s', self._url)

        connection_params = pika.URLParameters(self._url)
        if self.RABBIT_SERVER_CERT:
            os.environ.get('RABBIT_ROUTING_KEY')
            ssl_options = dict(
                ssl_version=ssl.PROTOCOL_TLSv1_2,
                ca_certs=self.RABBIT_SERVER_CERT)
            connection_params.ssl_options = ssl_options

        return pika.SelectConnection(connection_params,
                                     self.on_connection_open)

    def on_connection_open(self, unused_connection):
        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.

        :type unused_connection: pika.SelectConnection

        """
        LOGGER.info('Connection opened')
        self.add_on_connection_close_callback()
        self.open_channel()

    def add_on_connection_close_callback(self):
        """This method adds an on close callback that will be invoked by pika
        when RabbitMQ closes the connection to the publisher unexpectedly.

        """
        LOGGER.info('Adding connection close callback')
        self._connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.

        :param pika.connection.Connection connection: The closed connection obj
        :param int reply_code: The server provided reply_code if given
        :param str reply_text: The server provided reply_text if given

        """
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            LOGGER.warning('Connection closed, reopening in 5 seconds: (%s) %s',
                           reply_code, reply_text)
            self._connection.add_timeout(5, self.reconnect)

    def reconnect(self):
        """Will be invoked by the IOLoop timer if the connection is
        closed. See the on_connection_closed method.

        """
        # This is the old connection IOLoop instance, stop its ioloop
        self._connection.ioloop.stop()

        if not self._closing:

            # Create a new connection
            self._connection = self.connect()

            # There is now a new connection, needs a new ioloop to run
            self._connection.ioloop.start()

    def open_channel(self):
        """Open a new channel with RabbitMQ by issuing the Channel.Open RPC
        command. When RabbitMQ responds that the channel is open, the
        on_channel_open callback will be invoked by pika.

        """
        LOGGER.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.

        Since the channel is now open, we'll declare the exchange to use.

        :param pika.channel.Channel channel: The channel object

        """
        LOGGER.info('Channel opened')
        self._channel = channel

        # set qos so we only pull one message off the queue at a time and wait
        # until that's processed before doing the next
        channel.basic_qos(prefetch_count=self.RABBIT_PREFETCH)

        self.add_on_channel_close_callback()

        if not self.isQueueEstablished:
            self.setup_queue(self.QUEUE)
            self.isQueueEstablished = True

    def publish(self, exchange, routing_key, body, headers = {}):
        # This publish message should be compatible with both
        # topic exchanges and headers exchanges
        headers['routing-key'] = routing_key
        self._channel.basic_publish(exchange,
            routing_key=routing_key,
            body=body,
            properties=pika.BasicProperties(
                content_type='text/plain',
                headers = headers
            )
        )
        LOGGER.info('Published message on %s with routing key %s', exchange, routing_key)
        LOGGER.debug('Published message body: %s', body)

    def add_on_channel_close_callback(self):
        """This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.

        """
        LOGGER.info('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reply_code, reply_text):
        """Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.

        :param pika.channel.Channel: The closed channel
        :param int reply_code: The numeric reason the channel was closed
        :param str reply_text: The text reason the channel was closed

        """
        LOGGER.warning('Channel %i was closed: (%s) %s',
                       channel, reply_code, reply_text)
        self._connection.close()

    def setup_queue(self, queue_name):
        """Setup the queue on RabbitMQ by invoking the Queue.Declare RPC
        command. When it is complete, the on_queue_declareok method will
        be invoked by pika.

        :param str|unicode queue_name: The name of the queue to declare.

        """
        LOGGER.info('Declaring queue %s', queue_name)
        self._channel.queue_declare(self.on_queue_declareok, queue_name, durable=True, arguments={'x-max-priority': 10})

    def on_queue_declareok(self, method_frame):
        """Method invoked by pika when the Queue.Declare RPC call made in
        setup_queue has completed. In this method we will bind the queue
        and exchange together with the routing key by issuing the Queue.Bind
        RPC command. When this command is complete, the on_bindok method will
        be invoked by pika.

        :param pika.frame.Method method_frame: The Queue.DeclareOk frame

        """
        for exchange in self.EXCHANGES:
            LOGGER.info('Binding %s to %s with %s',
                        exchange, self.QUEUE, self.ROUTING_KEY)

            self._channel.queue_bind(self.on_bindok, self.QUEUE,
                                     exchange, self.ROUTING_KEY,
                                     arguments = self.options['queue_bind_arguments'])


    def on_bindok(self, unused_frame):
        """Invoked by pika when the Queue.Bind method has completed. At this
        point we will start consuming messages by calling start_consuming
        which will invoke the needed RPC commands to start the process.

        :param pika.frame.Method unused_frame: The Queue.BindOk response frame

        """
        LOGGER.info('Queue bound')
        if not self.isConsuming:
            self.start_consuming()
            self.isConsuming = True
            if self.on_connected_handler:
                self.on_connected_handler(self)

    def start_consuming(self):
        """This method sets up the consumer by first calling
        add_on_cancel_callback so that the object is notified if RabbitMQ
        cancels the consumer. It then issues the Basic.Consume RPC command
        which returns the consumer tag that is used to uniquely identify the
        consumer with RabbitMQ. We keep the value to use it when we want to
        cancel consuming. The on_message method is passed in as a callback pika
        will invoke when a message is fully received.

        """
        LOGGER.info('Issuing consumer related RPC commands')
        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(self.on_message,
                                                         self.QUEUE,
                                                         arguments=self.basic_consume_args)

    def add_on_cancel_callback(self):
        """Add a callback that will be invoked if RabbitMQ cancels the consumer
        for some reason. If RabbitMQ does cancel the consumer,
        on_consumer_cancelled will be invoked by pika.

        """
        LOGGER.info('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        """Invoked by pika when RabbitMQ sends a Basic.Cancel for a consumer
        receiving messages.

        :param pika.frame.Method method_frame: The Basic.Cancel frame

        """
        LOGGER.info('Consumer was cancelled remotely, shutting down: %r',
                    method_frame)
        if self._channel:
            self._channel.close()

    def on_message(self, unused_channel, basic_deliver, properties, body):
        """Invoked by pika when a message is delivered from RabbitMQ. The
        channel is passed for your convenience. The basic_deliver object that
        is passed in carries the exchange, routing key, delivery tag and
        a redelivered flag for the message. The properties passed in is an
        instance of BasicProperties with the message properties and the body
        is the message that was sent.

        :param pika.channel.Channel unused_channel: The channel object
        :param pika.Spec.Basic.Deliver: basic_deliver method
        :param pika.Spec.BasicProperties: properties
        :param str|unicode body: The message body

        """
        LOGGER.info('Received message # %s from %s',
                    basic_deliver.delivery_tag, basic_deliver.routing_key)
        LOGGER.debug('Message body %s', body)
        if not self.on_message_handler is None:
            def timer_tick():
                process_lock.acquire(self.RABBIT_MESSAGE_HANDLER_TIMEOUT)
                try:
                    self.acknowledge_message(basic_deliver.delivery_tag)
                    self.on_message_handler(partial(self.publish, basic_deliver.exchange, headers=properties.headers), body, properties)
                except Exception as e:
                    LOGGER.error('Error occurred while handling message: %s', e)
                    LOGGER.error('Stack trace: %s', traceback.print_exc())
                    print(e)
                process_lock.release()
            t = Timer(0.001, timer_tick)
            t.start()

            # This logic forces a timeout if the message handler takes longer
            # than x seconds
            t.join(self.RABBIT_MESSAGE_HANDLER_TIMEOUT)
            if t.is_alive():
                self.kill(basic_deliver.exchange, body, properties.headers)

    def kill(self, exchange, body = {}, headers = {}):
        """
        Method for hard killing the python process if it is running in docker
        """
        newBody = json.loads(body.decode())
        newBody['error'] = 'Thread timeout'
        newBody['lastSuccessfulKey'] = os.getenv('RABBIT_ROUTING_KEY', '')
        headers['routing-key'] = os.getenv('RABBIT_ERROR_ROUTING_KEY', 'error')
        LOGGER.error('Thread timeout')
        self.publish(exchange, headers['routing-key'], json.dumps(newBody), headers)
        def die():
            LOGGER.error('-'*50)
            LOGGER.error('Hard exiting docker due to message handler timeout')
            LOGGER.error('-'*50)
            subprocess.call('kill -INT 1', shell=True)
        t2 = Timer(5, die)
        t2.start()
        self.stop()

    def acknowledge_message(self, delivery_tag):
        """Acknowledge the message delivery from RabbitMQ by sending a
        Basic.Ack RPC method for the delivery tag.

        :param int delivery_tag: The delivery tag from the Basic.Deliver frame

        """
        LOGGER.info('Acknowledging message %s', delivery_tag)
        self._channel.basic_ack(delivery_tag)

    def stop_consuming(self):
        """Tell RabbitMQ that you would like to stop consuming by sending the
        Basic.Cancel RPC command.

        """
        if self._channel:
            LOGGER.info('Sending a Basic.Cancel RPC command to RabbitMQ')
            self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)

    def on_cancelok(self, unused_frame):
        """This method is invoked by pika when RabbitMQ acknowledges the
        cancellation of a consumer. At this point we will close the channel.
        This will invoke the on_channel_closed method once the channel has been
        closed, which will in-turn close the connection.

        :param pika.frame.Method unused_frame: The Basic.CancelOk frame

        """
        LOGGER.info('RabbitMQ acknowledged the cancellation of the consumer')
        self.close_channel()

    def close_channel(self):
        """Call to close the channel with RabbitMQ cleanly by issuing the
        Channel.Close RPC command.

        """
        LOGGER.info('Closing the channel')
        self._channel.close()

    def run(self):
        """Run the example consumer by connecting to RabbitMQ and then
        starting the IOLoop to block and allow the SelectConnection to operate.

        """
        self._connection = self.connect()
        self._connection.ioloop.start()

    def stop(self):
        """Cleanly shutdown the connection to RabbitMQ by stopping the consumer
        with RabbitMQ. When RabbitMQ confirms the cancellation, on_cancelok
        will be invoked by pika, which will then closing the channel and
        connection. The IOLoop is started again because this method is invoked
        when CTRL-C is pressed raising a KeyboardInterrupt exception. This
        exception stops the IOLoop which needs to be running for pika to
        communicate with RabbitMQ. All of the commands issued prior to starting
        the IOLoop will be buffered but not processed.

        """
        LOGGER.info('Stopping')
        self._closing = True
        self.stop_consuming()
        self._connection.ioloop.start()
        LOGGER.info('Stopped')

    def close_connection(self):
        """This method closes the connection to RabbitMQ."""
        LOGGER.info('Closing connection')
        self._connection.close()


    
Req.txt
-------
pika==0.12.0
pycparser==2.18
apache-libcloud==2.4.0
pycrypto==2.6.1
azure-storage-blob==2.1.0
    
Main.py
-------
#!/usr/bin/env python
import pika
import sys
import os
import logging
import json
import copy
from pwcutils import RabbitMQConsumer
from app import on_rabbitmq_connected, on_rabbitmq_message

RESULT_ROUTING_KEY = os.getenv('RABBIT_RESULT_ROUTING_KEY', 'result_routing_key')
LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
ROUTING_KEY = os.getenv('RABBIT_ROUTING_KEY', 'input_routing_key')
RABBIT_QUEUE_PRIORITY = int(os.getenv('RABBIT_QUEUE_PRIORITY', 0))
numeric_level = getattr(logging, os.getenv('LOG_LEVEL', 'WARNING'), None)
RABBIT_QUEUE_BIND_ARGUMENTS = json.loads(os.getenv('RABBIT_QUEUE_BIND_ARGUMENTS', '{}'))

def publish_result(publisher, msg, new_msg_props):
    msg.update(new_msg_props)
    publisher(RESULT_ROUTING_KEY, json.dumps(msg))

def main():
    logging.basicConfig(level=numeric_level, format=LOG_FORMAT)
    queue_bind_arguments = {
        "routing-key": ROUTING_KEY
    }
    queue_bind_arguments.update(RABBIT_QUEUE_BIND_ARGUMENTS)

    consumer = RabbitMQConsumer(
        os.environ.get('RABBIT_URL'),
        on_rabbitmq_message,
        # Use this as a headers exchange
        {
            "queue_bind_arguments": queue_bind_arguments,
            "on_connected": on_rabbitmq_connected,
            "basic_consume_args": {
                "x-priority": RABBIT_QUEUE_PRIORITY
            }
        }
    )
    try:
        consumer.run()
    except KeyboardInterrupt:
        consumer.stop()

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000)
    main()

