import inspect
import json
import logging
import os
import uuid
from typing import Callable

import boto3

ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_SQS", "")
SECRET_KEY = os.environ.get("AWS_SECRET_KEY_SQS", "")
QUEUE_URL = os.environ.get("QUEUE_URL", "")

logging.basicConfig(format="[%(levelname)s] [%(name)s] %(asctime)-15s  -> %(message)s")
LOGGER = logging.getLogger("SQS-SERVICE")

if os.environ.get("LEVEL", "DEBUG") == "DEBUG":
    LOGGER.setLevel(logging.DEBUG)
else:
    LOGGER.setLevel(logging.INFO)


class SQS:
    def __init__(self):
        self.sqs_client = boto3.client(
            "sqs",
            region_name="us-east-2",
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
        )

    def delete_message(self, receipt_handle):
        return self.sqs_client.delete_message(
            QueueUrl=QUEUE_URL,
            ReceiptHandle=receipt_handle,
        )

    def receive_messages(
        self, max_messages=None, wait_time=None, callback: Callable = None
    ) -> None:
        response = self.sqs_client.receive_message(
            QueueUrl=QUEUE_URL,
            MaxNumberOfMessages=max_messages or 1,
            WaitTimeSeconds=wait_time or 10,
        )

        messages = response.get("Messages", [])

        for message in messages:
            try:
                message_body = json.loads(message.get("Body"))
            except Exception as err_jsonify:
                message_body = message["Body"]
                LOGGER.error(f"Error trying to jsonify -> {err_jsonify}")

            if callback:
                self._callback_handler(callback, message_body)

            self.delete_message(message["ReceiptHandle"])

    def list_queues(self) -> dict:
        sqs_response = self.sqs_client.list_queues()

        if isinstance(sqs_response, dict):
            queues = sqs_response.get("QueueUrls", [])
            return {queue.split("/")[-1]: queue for queue in queues}
        return {}

    def send_message_to_topic(
        self, message_body, message_attributes=None, to_queue_url=None
    ) -> str:
        message_attributes = message_attributes or {}

        to_queue = to_queue_url or QUEUE_URL

        if to_queue.endswith(".fifo"):
            unique_key = uuid.uuid1().hex
            response = self.sqs_client.send_message(
                QueueUrl=to_queue,
                MessageAttributes=message_attributes,
                MessageGroupId=unique_key,
                MessageDeduplicationId=unique_key,
                MessageBody=json.dumps(message_body),
            )
        else:
            response = self.sqs_client.send_message(
                QueueUrl=to_queue,
                MessageAttributes=message_attributes,
                MessageBody=json.dumps(message_body),
            )

        LOGGER.debug(f"Message sent with ID -> {response['MessageId']}")
        return response["MessageId"]

    def _callback_handler(self, callback: Callable, message_body: dict):
        length_arguments_from_function = len(inspect.getfullargspec(callback).args)
        if length_arguments_from_function == 2:
            callback(message_body, self)
        else:
            LOGGER.warning(
                "The callback function must have first argument receiving a dict and second argument receiving an "
                "instance be receiving from SQS, like: "
                "handler(message_body: dict, sqs: SQS()) { # do some stuff with message_body } "
            )
