import boto3
import os
import json

QUEUE_URL = os.getenv("SQS_URL")


def entry(event, context):
    """
    Entry point, parse event and send message to the sqs queue
    """
    message = json.loads(event.get("body")).get("message")
    print(message)
    put_message(message)
    headers = {"Access-Control-Allow-Origin": "*"}
    body = '{"status": "OK"}'
    return {"headers": headers, "statusCode": 200, "body": body}


def send_email(event, context):
    """
    Receive message from sqs event and call email_message
    """
    message = json.loads(event.get("body")).get("message")
    print(email_message(message))
    return


def put_message(message):
    """
    Takes the message and sends to the sqs queue
    """
    try:
        SQS = boto3.client("sqs")
        body = {"message": message}
        body = str(body)
        print(SQS.send_message(QueueUrl=QUEUE_URL, MessageBody=body))
    except Exception:
        raise Exception("Failed to put message in queue!")


def email_message(message):
    """
    Sends the message with ses
    """
    SES = boto3.client("ses")
    SENDER_EMAIL = os.getenv("SENDER_EMAIL") or "test@example.com"
    SENDTO_EMAIL = os.getenv("SENDTO_EMAIL") or "test_to@example.com"
    response = SES.send_email(
        Destination={
            "ToAddresses": [SENDTO_EMAIL],
        },
        Message={
            "Body": {
                "Text": {
                    "Charset": "UTF-8",
                    "Data": message,
                },
            },
            "Subject": {
                "Charset": "UTF-8",
                "Data": "email subject string",
            },
        },
        Source=SENDER_EMAIL,
    )
    return response
