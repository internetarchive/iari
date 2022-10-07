import json
from typing import Optional

from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from pika.adapters.blocking_connection import BlockingChannel
from pydantic import validate_arguments

import config
from src.helpers.console import console
from src.models.message import Message
from src.wcd_base_model import WcdBaseModel


class NoChannelError(BaseException):
    pass


class WorkQueue(WcdBaseModel):
    """This models the RabbitMQ article queue
    We publish to this queue when ingesting page updates
    and when receiving a WDQID via the wikicitaitons-api"""

    connection: Optional[BlockingConnection]
    channel: Optional[BlockingChannel]
    queue_name: str = "article_queue"

    class Config:
        arbitrary_types_allowed = True

    @validate_arguments
    def publish(self, message: bytes):
        """This publishes a message to the default work queue"""
        self.__connect__()
        self.__setup_channel__()
        self.__create_queue__()
        self.__send_message__(message=message)
        self.__close_connection__()

    def __connect__(self):
        self.connection = BlockingConnection(
            ConnectionParameters(
                "localhost",
                credentials=PlainCredentials(
                    username=config.rabbitmq_username, password=config.rabbitmq_password
                ),
            )
        )

    def __setup_channel__(self):
        self.channel = self.connection.channel()

    def __create_queue__(self):
        self.channel.queue_declare(queue=self.queue_name)

    def __close_connection__(self):
        self.connection.close()

    def __send_message__(self, message: bytes):
        if self.channel:
            self.channel.basic_publish(
                exchange="", routing_key=self.queue_name, body=message
            )
            print(" [x] Sent message!")
        else:
            raise NoChannelError()

    def listen_to_queue(self):
        """This function is run by the wcdimportbot worker
        There can be multiple workers running at the same time listening to the work queue"""

        def callback(channel, method, properties, body):
            print(" [x] Received %r" % body)
            # Parse into OOP and do the work
            data = json.loads(body)
            message = Message(**data)
            console.print(message.dict())
            message.process_data()

        self.__connect__()
        self.__setup_channel__()
        self.__create_queue__()
        self.channel.basic_consume(
            queue=self.queue_name, auto_ack=True, on_message_callback=callback
        )
        print(" [*] Waiting for messages. To exit press CTRL+C")
        self.channel.start_consuming()
