import unittest
import boto3
from moto import mock_sqs, mock_ses
import handler

API_GW_EVENT = {
    "resource": "/messsages",
    "path": "/messsages",
    "httpMethod": "POST",
    "headers": {
        "Accept": "*/*",
        "CloudFront-Forwarded-Proto": "https",
        "CloudFront-Is-Desktop-Viewer": "true",
        "CloudFront-Is-Mobile-Viewer": "false",
        "CloudFront-Is-SmartTV-Viewer": "false",
        "CloudFront-Is-Tablet-Viewer": "false",
        "CloudFront-Viewer-Country": "US",
        "content-type": "application/x-www-form-urlencoded",
        "Host": "abc123.execute-api.us-west-2.amazonaws.com",
        "User-Agent": "curl/7.54.0",
        "Via": "2.0 3f7e5e686bf8f19b9c786efbe99c7589.cloudfront.net (CloudFront)",
        "X-Amz-Cf-Id": "VOYFpRFqcCEuPO6UBHYbWgzdg-BQaPhOFD7CYFK6jLEsM-y8xRbdUA==",
        "X-Amzn-Trace-Id": "Root=1-5fdd5a9d-2803b33a630ca3047320a263",
        "X-Forwarded-For": "1.2.3.4, 5.6.7.8",
        "X-Forwarded-Port": "443",
        "X-Forwarded-Proto": "https",
    },
    "multiValueHeaders": {
        "Accept": ["*/*"],
        "CloudFront-Forwarded-Proto": ["https"],
        "CloudFront-Is-Desktop-Viewer": ["true"],
        "CloudFront-Is-Mobile-Viewer": ["false"],
        "CloudFront-Is-SmartTV-Viewer": ["false"],
        "CloudFront-Is-Tablet-Viewer": ["false"],
        "CloudFront-Viewer-Country": ["US"],
        "content-type": ["application/x-www-form-urlencoded"],
        "Host": ["abc123f.execute-api.us-west-2.amazonaws.com"],
        "User-Agent": ["curl/7.54.0"],
        "Via": ["2.0 3f7e5e686bf8f19b9c786efbe99c7589.cloudfront.net (CloudFront)"],
        "X-Amz-Cf-Id": ["VOYFpRFqcCEuPO6UBHYbWgzdg-BQaPhOFD7CYFK6jLEsM-y8xRbdUA=="],
        "X-Amzn-Trace-Id": ["Root=1-fjfjflfjslfjslfjsf34u242u4024a263"],
        "X-Forwarded-For": ["1.2.3.4, 5.6.7.8"],
        "X-Forwarded-Port": ["443"],
        "X-Forwarded-Proto": ["https"],
    },
    "queryStringParameters": None,
    "multiValueQueryStringParameters": None,
    "pathParameters": None,
    "stageVariables": None,
    "requestContext": {
        "resourceId": "abc123",
        "resourcePath": "/messsages",
        "httpMethod": "POST",
        "extendedRequestId": "XxsYsF25PHcF4sQ=",
        "requestTime": "19/Dec/2020:01:42:53  0000",
        "path": "/dev/messsages",
        "accountId": "1234567890",
        "protocol": "HTTP/1.1",
        "stage": "dev",
        "domainPrefix": "abc123",
        "requestTimeEpoch": 1608342173987,
        "requestId": "9a703af5-fe0a-4515-b7a1-fb95c09b0086",
        "identity": {
            "cognitoIdentityPoolId": None,
            "accountId": None,
            "cognitoIdentityId": None,
            "caller": None,
            "sourceIp": "1.2.3.4",
            "principalOrgId": None,
            "accessKey": None,
            "cognitoAuthenticationType": None,
            "cognitoAuthenticationProvider": None,
            "userArn": None,
            "userAgent": "curl/7.54.0",
            "user": None,
        },
        "domainName": "abc123.execute-api.us-west-2.amazonaws.com",
        "apiId": "abc123",
    },
    "body": '{"message":"Hello AWS!"}',
    "isBase64Encoded": False,
}
SQS_EVENT = {
    "Records": [
        {
            "messageId": "12345678901234567890",
            "receiptHandle": "12345678901234567890",
            "body": "Hello AWS!",
            "attributes": {
                "ApproximateReceiveCount": "1",
                "SentTimestamp": "1608790761621",
                "SenderId": "ABCDEFGHIJKLMNOP:python-sqs-lambda-dev-api_gw_post_message",
                "ApproximateFirstReceiveTimestamp": "1608790761625",
            },
            "messageAttributes": {},
            "md5OfBody": "11234567890123456789",
            "eventSource": "aws:sqs",
            "eventSourceARN": "arn:aws:sqs:us-west-1:1234567890:python-first-queue",
            "awsRegion": "us-west-1",
        }
    ]
}


class TestHandler(unittest.TestCase):
    @mock_sqs
    def test_message_to_sqs_queue(self):
        print("\nRunning test_message_to_sqs_queue")
        sqs = boto3.resource("sqs")
        queue = sqs.create_queue(QueueName="test-sqs-message")
        handler.QUEUE_URL = queue.url
        message = "Testing with a valid message"
        expected_message = str(message)
        handler.message_to_sqs_queue(message)
        sqs_messages = queue.receive_messages()
        assert (
            sqs_messages[0].body == expected_message
        ), "Message does not match expected"
        assert len(sqs_messages) == 1, "Expected exactly one message in SQS"

    def test_message_to_sqs_queue_exception(self):
        print("\nRunning test_message_to_sqs_queue_exception")
        queue = None
        handler.QUEUE_URL = queue
        message = None
        self.assertRaises(Exception, handler.message_to_sqs_queue, message)

    @mock_sqs
    def test_api_gw_post_message(self):
        print("\nRunning test_api_gw_post_message")
        sqs = boto3.resource("sqs")
        queue = sqs.create_queue(QueueName="test-sqs-message")
        handler.QUEUE_URL = queue.url
        headers = {"Access-Control-Allow-Origin": "*"}
        context = {}
        body = '{"status": "OK"}'
        expected_data = {"headers": headers, "statusCode": 200, "body": body}
        result = handler.api_gw_post_message(API_GW_EVENT, context)
        assert result == expected_data

    @mock_ses
    def test_send_email_ses(self):
        print("\nRunning test_send_email_ses")
        ses = boto3.client("ses")
        ses.verify_email_address(EmailAddress="test@example.com")
        handler.send_email_ses.ses = ses
        message = "Testing with a valid message"
        response = handler.send_email_ses(message)
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    @mock_ses
    def test_sqs_queue_event_handler(self):
        print("\nRunning test_sqs_queue_event_handler")
        ses = boto3.client("ses")
        ses.verify_email_address(EmailAddress="test@example.com")
        handler.send_email_ses.ses = ses
        context = {}
        expected_result = {"status": "OK"}
        result = handler.sqs_queue_event_handler(SQS_EVENT, context)
        assert result == expected_result
