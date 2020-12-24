import json
import os
import boto3

QUEUE_URL = os.getenv("SQS_URL")


def api_gw_post_message(event, context):
    """
    Receive http PUT from the Api GW. Parse message and place in SQS queue
    """
    message = json.loads(event.get("body")).get("message")
    print(message)
    message_to_sqs_queue(message)
    headers = {"Access-Control-Allow-Origin": "*"}
    body = '{"status": "OK"}'
    return {"headers": headers, "statusCode": 200, "body": body}


def message_to_sqs_queue(message):
    """
    Takes the message and sends to the sqs queue

    Parameters:
        message (str): Message to be sent the queue
    """
    try:
        sqs = boto3.client("sqs")
        # Shows up as - "body": "Hello AWS!" - in the message
        # This should be done better
        body = str(message)
        print(sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=body))
    except Exception:
        raise Exception("Failed to put message in queue!")


def sqs_queue_event_handler(event, context):
    """
    Triggered via messages in the SQS queue. Parses the queue's message,
    and grabs our message. We take the message and call send_email_ses(message)
    """
    print(event)
    for record in event["Records"]:
        message = record.get("body")
        print(message)
        print(send_email_ses(message))
    return {"status": "OK"}


def send_email_ses(message):
    """
    Sends the message with ses

    Parameters:
        message (str): Message to be sent via SES
    """
    ses = boto3.client("ses")
    sender_email = os.getenv("SENDER_EMAIL") or "test@example.com"
    sendto_email = os.getenv("SENDTO_EMAIL") or "test_to@example.com"
    response = ses.send_email(
        Destination={
            "ToAddresses": [sendto_email],
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
        Source=sender_email,
    )
    return response
