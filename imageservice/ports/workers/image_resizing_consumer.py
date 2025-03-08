import logging
import os
import threading

import click

from imageservice.domain.http import HTTP
from imageservice.services.sqs import SQS
from imageservice.usecases.resize_img_url_and_itunes_image import (
    ResizingImageUrlAndItunesImage,
)

POSTBACK_SECRET_KEY = os.environ.get(
    "POSTBACK_SECRET_KEY", "47/:6WT?v5edl|W}Dt&#TK5.hwe>3,"
)

CALLS_TO_UPDATE_LIST_SQS_QUEUES = os.environ.get(
    "NUMBER_CALLS_TO_UPDATE_SQS_QUEUE_LIST", 100000
)
SQS_QUEUE_LIST: dict = {}
count_calls = 0
signal_to_stop = False

logging.basicConfig(format="[%(levelname)s] [%(name)s] %(asctime)-15s  -> %(message)s")
LOGGER = logging.getLogger("SQS-CONSUMER")

if os.environ.get("LEVEL", "DEBUG") == "DEBUG":
    LOGGER.setLevel(logging.DEBUG)
else:
    LOGGER.setLevel(logging.INFO)


def _handler(message_body: dict, sqs: SQS):
    LOGGER.debug(f"Message received: {message_body}")

    redirect_queue = message_body.get("redirect_queue")
    postback_url = message_body.get("postback_url")
    image_url = message_body.get("image_url")
    itunes_image = message_body.get("itunes_image")

    if not redirect_queue and not postback_url:
        LOGGER.debug("No queue or postback url was provided. So, stopping process.")
        return

    try:
        images_info = ResizingImageUrlAndItunesImage.resize_image_and_return_info(
            image_url, itunes_image, message_body.get("bucket_name")
        )
        message_body.update(images_info)

        # Redirect to a queue if it exists
        if redirect_queue in SQS_QUEUE_LIST:
            LOGGER.debug(f"Sending message to [{redirect_queue}]...")
            sqs.send_message_to_topic(
                message_body=message_body,
                to_queue_url=SQS_QUEUE_LIST[redirect_queue],
            )

        # Sending info to postback url
        if postback_url:
            message_body["postback_secret_key"] = POSTBACK_SECRET_KEY
            result = HTTP.send_postback(postback_url, message_body)
            LOGGER.debug(
                f"Sending message to postback_url [{postback_url}]. Was it sent?  {result} ..."
            )

    except Exception as err_handler:
        LOGGER.error(f"Error in the handlers -> {err_handler}")


def _update_calls_and_sqs_queue_list_if_necessary(sqs: SQS):
    global CALLS_TO_UPDATE_LIST_SQS_QUEUES, count_calls, SQS_QUEUE_LIST

    try:
        count_calls += 1

        if count_calls % CALLS_TO_UPDATE_LIST_SQS_QUEUES == 0:
            LOGGER.info("Updating SQS list queues...")
            count_calls = 0
            SQS_QUEUE_LIST = sqs.list_queues()
    except Exception as update_sqs_list_error:
        LOGGER.error(update_sqs_list_error)


def _worker(sqs):
    global signal_to_stop

    # Worker that checks if the queue has new messages.
    while not signal_to_stop:
        try:
            sqs.receive_messages(callback=_handler)
            _update_calls_and_sqs_queue_list_if_necessary(sqs)
        except Exception as err:
            LOGGER.info(err)


@click.command()
@click.option(
    "-w",
    "--num-workers",
    default=1,
    show_default=True,
    type=int,
    help="Number of workers to be enabled.",
)
def main(num_workers):
    LOGGER.info(f"STARTING with {num_workers} worker(s).")
    sqs = SQS()

    global SQS_QUEUE_LIST
    SQS_QUEUE_LIST = sqs.list_queues()

    if num_workers == 1:
        _worker(sqs)
    else:
        for num in range(num_workers):
            thread = threading.Thread(target=_worker, args=(sqs,))
            thread.name = f"Thread-{num}"
            thread.start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        signal_to_stop = True
        LOGGER.info("Graceful exit.")
