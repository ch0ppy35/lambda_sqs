import unittest
import boto3
from moto import mock_sqs, mock_ses
import handler

event = {
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
    "body": '{"message":"hi"}',
    "isBase64Encoded": False,
}


class TestHandler(unittest.TestCase):
    @mock_sqs
    def test_put_message(self):
        SQS = boto3.resource("sqs")
        queue = SQS.create_queue(QueueName="test-sqs-message")
        handler.QUEUE_URL = queue.url
        message = "Testing with a valid message"
        expected_message = {"message": message}
        expected_message = str(expected_message)
        handler.put_message(message)
        sqs_messages = queue.receive_messages()
        assert (
            sqs_messages[0].body == expected_message
        ), "Message does not match expected"
        assert len(sqs_messages) == 1, "Expected exactly one message in SQS"

    @mock_sqs
    def test_entry(self):
        SQS = boto3.resource("sqs")
        queue = SQS.create_queue(QueueName="test-sqs-message")
        handler.QUEUE_URL = queue.url
        headers = {"Access-Control-Allow-Origin": "*"}
        context = {}
        body = '{"status": "OK"}'
        expected_data = {"headers": headers, "statusCode": 200, "body": body}
        result = handler.entry(event, context)
        assert result == expected_data

    @mock_ses
    def test_email_message(self):
        SES = boto3.client("ses")
        SES.verify_email_address(EmailAddress="test@example.com")
        handler.email_message.SES = SES
        message = "Testing with a valid message"
        response = handler.email_message(message)
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
