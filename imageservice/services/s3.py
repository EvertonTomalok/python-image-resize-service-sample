import logging
import os

import boto3
from boto3.s3.transfer import S3Transfer

from imageservice.utils.strings import normalize_text

logging.basicConfig(format="[%(levelname)s] [%(name)s] %(asctime)-15s  -> %(message)s")
LOGGER = logging.getLogger("SQS-CONSUMER")

if os.environ.get("LEVEL", "DEBUG") == "DEBUG":
    LOGGER.setLevel(logging.DEBUG)
else:
    LOGGER.setLevel(logging.INFO)

ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_S3", "")
SECRET_KEY = os.environ.get("AWS_ACCESS_KEY_SQS", "")

credentials = {
    "aws_access_key_id": ACCESS_KEY,
    "aws_secret_access_key": SECRET_KEY,
}


class S3:
    @staticmethod
    def send_file(file_name, bucket, object_name=None, public=False) -> None:
        client = boto3.client("s3", "us-east-2", **credentials)

        object_name = object_name or file_name
        transfer = S3Transfer(client)
        extra_args = {"ACL": "public-read"} if public else {}

        transfer.upload_file(file_name, bucket, object_name, extra_args=extra_args)

    @staticmethod
    def send_resized_public_image(file_name, bucket_path=None, public=False) -> dict:

        bucket = "images-ch"
        if bucket_path:
            cleaned_bucket_name = (
                bucket_path.strip()
                .replace("/", "--")
                .replace(" ", "_")
                .replace("?", "-")
                .replace("&", "-")
                .upper()
            )
            bucket_path = f"images-resized/{normalize_text(cleaned_bucket_name)}/"
        else:
            bucket_path = "images-resized/custom/"

        object_name = bucket_path + file_name
        client = boto3.client("s3", "us-east-2", **credentials)
        transfer = S3Transfer(client)
        extra_args = {"ACL": "public-read"} if public else {}

        transfer.upload_file(file_name, bucket, object_name, extra_args=extra_args)

        return {
            "url": (
                "%s/%s/%s" % (client.meta.endpoint_url, bucket, object_name)
                if public
                else ""
            ),
            "bucket_path": bucket_path,
        }
