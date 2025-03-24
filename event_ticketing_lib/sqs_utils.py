import boto3
from config import REGION_NAME, SQS_QUEUE_URL

def send_message_to_sqs(message_body):
    try:
        sqs = boto3.client('sqs', region_name=REGION_NAME)
        response = sqs.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=message_body
        )
        print("Message sent to SQS:", response['MessageId'])
    except Exception as e:
        print("Error sending message to SQS:", str(e))
