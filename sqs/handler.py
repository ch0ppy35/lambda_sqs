import boto3
import os
import json

QUEUE_URL = os.getenv("SQS_URL")


def entry(event, context):
    # print(event)
    message = json.loads(event.get("body")).get("message")
    print(message)
    put_message(message)
    headers = {"Access-Control-Allow-Origin": "*"}
    body = '{"status": "OK"}'
    return {"headers": headers, "statusCode": 200, "body": body}


def send_email(event, context):
    # TODO Build this
    print(event)
    return


def put_message(message):
    try:
        SQS = boto3.client("sqs")
        body = {"message": message}
        body = str(body)
        print(SQS.send_message(QueueUrl=QUEUE_URL, MessageBody=body))
    except Exception:
        raise Exception("Failed to put message in queue!")
