# # pylint: disable=C0111,C0103,R0205
#
# import functools
# import json
# import logging
# import threading
# from typing import Any, List, Optional
#
# from pika import BlockingConnection, ConnectionParameters, PlainCredentials
# from pika.adapters.blocking_connection import BlockingChannel
# from pika.exceptions import AMQPConnectionError
# from pydantic import validate_arguments
#
# import config
# from src.helpers.console import console
# from src.models.exceptions import NoChannelError
# from src.models.message import Message
# from src.models.wikibase import Wikibase
# from src.wcd_base_model import WcdBaseModel
#
# logger = logging.getLogger(__name__)
#
#
# class WorkQueue(WcdBaseModel):
#     """This models the RabbitMQ article queue
#     We publish to this queue when ingesting page updates
#     and when receiving a title via the wikicitaitons-api
#     add-job endpoint
#
#     This class is partly based on https://github.com/pika/pika/blob/1.0.1/examples/basic_consumer_threaded.py"""
#
#     connection: Optional[BlockingConnection]
#     channel: Optional[BlockingChannel]
#     queue_name: str = "article_queue"
#     wikibase: Wikibase
#     testing: bool = False
#
#     class Config:
#         arbitrary_types_allowed = True
#
#     @validate_arguments
#     def publish(self, message: Message) -> bool:
#         """This publishes a message to the default work queue"""
#         try:
#             self.__connect__()
#         except AMQPConnectionError:
#             return False
#         self.__setup_channel__()
#         self.__create_queue__()
#         self.__send_message__(message=message)
#         self.__close_connection__()
#         return True
#
#     # @backoff.on_exception(backoff.expo, AMQPConnectionError, max_time=60)
#     def __connect__(self):
#         # credentials = pika.PlainCredentials('guest', 'guest')
#         # # Note: sending a short heartbeat to prove that heartbeats are still
#         # # sent even though the worker simulates long-running work
#         # parameters = pika.ConnectionParameters(
#         #     'localhost', credentials=credentials, heartbeat=5)
#         # connection = pika.BlockingConnection(parameters)
#
#         self.connection = BlockingConnection(
#             ConnectionParameters(
#                 "localhost",
#                 credentials=PlainCredentials(
#                     username=config.rabbitmq_username, password=config.rabbitmq_password
#                 ),
#             )
#         )
#
#     def __setup_channel__(self):
#         """This is idempotent :)"""
#         self.channel = self.connection.channel()
#         self.channel.exchange_declare(
#             exchange="test_exchange",
#             exchange_type="direct",
#             passive=False,
#             durable=True,
#             auto_delete=False,
#         )
#         self.channel.queue_declare(queue="standard", auto_delete=True)
#         self.channel.queue_bind(
#             queue="standard", exchange="test_exchange", routing_key="standard_key"
#         )
#         # Note: prefetch is set to 1 here as an example only and to keep the number of threads created
#         # to a reasonable amount. In production you will want to test with different prefetch values
#         # to find which one provides the best performance and usability for your solution
#         self.channel.basic_qos(prefetch_count=1)
#
#     def __create_queue__(self):
#         """This is idempotent :)"""
#         self.channel.queue_declare(queue=self.queue_name)
#
#     def __close_connection__(self):
#         self.connection.close()
#
#     @validate_arguments
#     def __send_message__(self, message: Message):
#         if self.channel:
#             message_bytes = bytes(json.dumps(message.json()), "utf-8")
#             self.channel.basic_publish(
#                 exchange="", routing_key=self.queue_name, body=message_bytes
#             )
#             print(" [x] Sent message!")
#         else:
#             raise NoChannelError()
#
#     def listen_to_queue(self, testing: bool = False):
#         """This function is run by the wcdimportbot worker
#         There can be multiple workers running at the same
#         time listening to the work queue
#
#         We use threading to avoid the worker quitting
#         because it cannot keep the connection to
#         rabbitmq open during the work and errors out"""
#         if testing and not self.cache:
#             self.__setup_cache__()
#         if not self.cache:
#             raise ValueError("self.cache was None")
#         self.__connect__()
#         self.__setup_channel__()
#         self.__create_queue__()
#
#         if not self.testing and self.channel and self.connection:
#             print(" [*] Waiting for messages. To exit press CTRL+C")
#             threads: List[Any] = []
#             on_message_callback = functools.partial(
#                 self.__on_message__, args=(self.connection, threads)
#             )
#             self.channel.basic_consume(queue=self.queue_name, on_message_callback=on_message_callback)  # type: ignore
#
#             try:
#                 self.channel.start_consuming()
#             except KeyboardInterrupt:
#                 self.channel.stop_consuming()
#
#             # Wait for all to complete
#             for thread in threads:
#                 thread.join()
#
#             self.connection.close()
#         else:
#             if not self.channel:
#                 raise ValueError("self.channel was None")
#             if not self.connection:
#                 raise ValueError("self.connection was None")
#
#     @staticmethod
#     def __ack_message__(ch, delivery_tag):
#         """Note that `ch` must be the same pika channel instance via which
#         the message being ACKed was retrieved (AMQP protocol constraint).
#         """
#         if ch.is_open:
#             ch.basic_ack(delivery_tag)
#         else:
#             # Channel is already closed, so we can't ACK this message;
#             # log and/or do something that makes sense for your app in this case.
#             logger.error("channel is already closed")
#             pass
#
#     def __do_work__(self, conn, ch, delivery_tag, body):
#         if not self.cache:
#             raise ValueError("self.cache was None")
#         thread_id = threading.get_ident()
#         logger.info(
#             "Thread id: %s Delivery tag: %s Message body: %s",
#             thread_id,
#             delivery_tag,
#             body,
#         )
#         # Parse into OOP and do the work
#         decoded_body = body.decode("utf-8")
#         json_data_string = json.loads(decoded_body)
#         json_data_dict = json.loads(json_data_string)
#         if config.loglevel == logging.DEBUG:
#             console.print(json_data_dict)
#         message = Message(**json_data_dict)
#         message.cache = self.cache
#         print(f" [x] Received {message.title} job for {message.wikibase.title}")
#         if config.loglevel == logging.DEBUG:
#             console.print(message.dict())
#         message.process_data()
#
#         cb = functools.partial(self.__ack_message__, ch, delivery_tag)
#         conn.add_callback_threadsafe(cb)
#
#     def __on_message__(self, ch, method_frame, _header_frame, body, args):
#         (conn, thrds) = args
#         delivery_tag = method_frame.delivery_tag
#         t = threading.Thread(
#             target=self.__do_work__, args=(conn, ch, delivery_tag, body)
#         )
#         t.start()
#         thrds.append(t)
