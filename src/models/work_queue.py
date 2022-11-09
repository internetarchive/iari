import json
import logging
from typing import Optional

from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import AMQPConnectionError
from pydantic import validate_arguments

import config
from src.helpers.console import console
from src.models.exceptions import NoChannelError
from src.models.message import Message
from src.models.wikibase import Wikibase
from src.wcd_base_model import WcdBaseModel

logger = logging.getLogger(__name__)


class WorkQueue(WcdBaseModel):
    """This models the RabbitMQ article queue
    We publish to this queue when ingesting page updates
    and when receiving a title via the wikicitaitons-api
    add-job endpoint"""

    connection: Optional[BlockingConnection]
    channel: Optional[BlockingChannel]
    queue_name: str = "article_queue"
    wikibase: Wikibase
    testing: bool = False

    class Config:
        arbitrary_types_allowed = True

    @validate_arguments
    def publish(self, message: Message) -> bool:
        """This publishes a message to the default work queue"""
        try:
            self.__connect__()
        except AMQPConnectionError:
            return False
        self.__setup_channel__()
        self.__create_queue__()
        self.__send_message__(message=message)
        self.__close_connection__()
        return True

    # @backoff.on_exception(backoff.expo, AMQPConnectionError, max_time=60)
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
        """This is idempotent :)"""
        self.channel = self.connection.channel()

    def __create_queue__(self):
        """This is idempotent :)"""
        self.channel.queue_declare(queue=self.queue_name)

    def __close_connection__(self):
        self.connection.close()

    @validate_arguments
    def __send_message__(self, message: Message):
        if self.channel:
            message_bytes = bytes(json.dumps(message.json()), "utf-8")
            self.channel.basic_publish(
                exchange="", routing_key=self.queue_name, body=message_bytes
            )
            print(" [x] Sent message!")
        else:
            raise NoChannelError()

    def listen_to_queue(self):
        """This function is run by the wcdimportbot worker
        There can be multiple workers running at the same
        time listening to the work queue"""

        def callback(channel, method, properties, body):
            logger.debug(" [x] Received %r" % body)
            # Parse into OOP and do the work
            decoded_body = body.decode("utf-8")
            json_data_string = json.loads(decoded_body)
            json_data_dict = json.loads(json_data_string)
            if config.loglevel == logging.DEBUG:
                console.print(json_data_dict)
            message = Message(**json_data_dict)
            print(f" [x] Received {message.title} job for {message.wikibase.title}")
            if config.loglevel == logging.DEBUG:
                console.print(message.dict())
            message.process_data()

        self.__connect__()
        self.__setup_channel__()
        self.__create_queue__()
        self.channel.basic_consume(
            queue=self.queue_name, auto_ack=True, on_message_callback=callback
        )
        if not self.testing:
            print(" [*] Waiting for messages. To exit press CTRL+C")
            self.channel.start_consuming()
