# image-service
Image Processing Microservice Repository

# Setup

This project includes Makefile recipes that automate certain tasks. Makefiles are functional scripts for UNIX-based operating systems.

## Setting up the project

Run:

- `make setup`

To set up including development libraries, run:

- `make setup-dev`

# Script for Resizing New Channel Images

## How to Schedule a CRON JOB

We use PM2 to assist in scheduling scripts. If you need to install it, check this [link](https://pm2.keymetrics.io/docs/usage/quick-start/#installation)

### Creating the cron job for resizing channel images

Use the following command to instruct the OS to run the script daily at 1 AM.

- `make pm2-script-resize-images-from-channel`

or

- `pm2 start "export ENVIRONMENT=PRODUCTION && poetry run python -m scripts.resize_images_from_channel_collection" --no-autorestart --cron '0 1 * * *' --name 'resize-image-from-channel'`

### Removing the cron job for resizing channel images

Use the following command:

- `make pm2-delete-script-resize-images-from-channel`

or

- `pm2 delete resize-image-from-channel`

### Adding the cron job for resizing episode images

Use the following command:

- `make pm2-script-resize-images-from-episodes`

or

- `pm2 start "export ENVIRONMENT=PRODUCTION && poetry run python -m scripts.resize_images_from_episodes_collection" --no-autorestart --cron '0 1 * * *' --name 'resize-image-from-episodes'`

### Removing the cron job for resizing episode images

Use the following command:

- `make pm2-delete-script-resize-images-from-episodes`

or

- `pm2 delete resize-image-from-episodes`

# Image Resizing Microservice

Below is the architectural sketch of the microservice:

![IMAGES SERVICE](./doc/IMAGES_SERVICE.jpg)

## Sending a Message to the Queue

Below is an example of a basic dictionary that should be sent to the queue:

```
{
    "image_url": "http://imagem.com.br/img.jpg",
    "itunes_image": "http://itunes-imagem.com.br/img.jpg",
    "bucket_name": "Bucket name where the image should be saved", # Optional
    "redirect_queue": "QueueSQS", # If the queue does not exist, the message will not be redirected
    "postback_url": "http://callbackurl.com/postback", 
    ... (any other necessary fields to be passed to the next queue or postback URL)
}
```

### Essential Fields:

- `image_url` or `itunes_image`, or both (if none are provided, processing will not occur)
- `redirect_queue` or `postback_url`, or both (if none are provided, processing will not occur)

### Example of Usage with Embedded S3 Service:

```
from imageservice.services.sqs import SQS

sqs = SQS()

sqs.send_message_to_topic(
    {
        "_id": ObjectId("SomeObjectID"),
        "image_url": "http://someimage.com/img.png",
        "bucket_name": "Test Bucket",
        "redirect_queue": "ChannelImages",
        "postback_url": "http://mycallbackurl.com/postback",
    }
)
```

## Capturing Saved Image Path via Postback

If a postback URL was provided with the message to the queue, after processing, a POST request will be sent containing all received message data, including the paths where images were saved in various formats, along with a `postback_secret_key` value of `47/:6WT?v5edl|W}Dt&#TK5.hwe>3,`, to verify the request originated from the microservice.

### Example of Message Sent via Postback

Fields added in the postback: `image_url_info` (if provided in the queue message), `itunes_image_info` (if provided in the queue message), and `postback_secret_key`.

```
{
   "image_url":"http://i1.sndcdn.com/avatars-000668567399-di3yod-original.jpg",
   "bucket_name":"TEST",
   "redirect_queue":"ChannelImages",
   "postback_url":"http://my-postback-url/postback",
   "image_url_info":{
      "50x50":{
         "url":"https://s3.us-east-2.amazonaws.com/images-ch/images-resized/TEST/975bfd4caa0d11ebb394f36767fff8ec_50x50.jpeg",
         "bucket_path":"images-resized/TEST/"
      },
      "250X250":{
         "url":"https://s3.us-east-2.amazonaws.com/images-ch/images-resized/TEST/975bfd4caa0d11ebb394f36767fff8ec_250X250.jpeg",
         "bucket_path":"images-resized/TEST/"
      },
      "800x800":{
         "url":"https://s3.us-east-2.amazonaws.com/images-ch/images-resized/TEST/975bfd4caa0d11ebb394f36767fff8ec_800x800.jpeg",
         "bucket_path":"images-resized/TEST/"
      }
   },
   "postback_secret_key":"47/:6WT?v5edl|W}Dt&#TK5.hwe>3,"
}
```

![MESSAGE_POSTBACK](./doc/MESSAGE_POSTBACK.jpg)

# Activating the Microservice:

Run the following command:

- `make pm2-image-consumer`

or

- `pm2 start "export QUEUE_URL=https://sqs.us-east-2.amazonaws.com/328097268885/ImageQueue.fifo && export LEVEL=INFO && poetry run python -m imageservice.ports.workers.image_resizing_consumer -w 1" --name 'image-consumer'`

If a project named `image-consumer` is already running (check with `pm2 status`), use the command below:

- `make pm2-restart-image-consumer`

# Deactivating the Microservice:

Run the following command:

- `make pm2-delete-image-consumer`

or

- `pm2 delete image-consumer`

# Environment variables

| var | Default | description |
|---|---|---|
| AWS_ACCESS_KEY_S3 | *** | Access key value for the AWS S3 IAM user  |
| AWS_SECRET_KEY_S3 | *** | Secret key value for the AWS S3 IAM user  |
| AWS_ACCESS_KEY_SQS | *** | Key value for the AWS SQS IAM user |
| AWS_SECRET_KEY_SQS | *** | Secret key value for the AWS SQS IAM user  |
| QUEUE_URL |  https://sqs.us-east-2.amazonaws.com/328097268885/ImageQueueTest.fifo | Queue for reading messages, also used as the default when sending a message (if no parameter is received in the function)|
| LEVEL  | DEBUG | Value assumed for LOGGING |
| CALLS_TO_UPDATE_LIST_SQS_QUEUES | 100000 | Number of times `receive_messages` must be executed to update the queue list in SQS |
| MONGO_URL | mongodb+srv://---:---@cluster.mongodb.net/db | Access URL for MongoDB |
| DB_ENVIRONMENT | DEVELOP  | Switches database access between prod/dev if `MONGO_URL` is not set |
