import boto3
import time
from config import sqs_queue_url

# Initialize SQS client
sqs = boto3.client('sqs')

print("🎧 Listening to SQS messages...")

while True:
    response = sqs.receive_message(
        QueueUrl=sqs_queue_url,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=10
    )

    messages = response.get('Messages', [])
    for message in messages:
        print("🔔 New SQS Message Received:")
        print("📦 Raw message body:", message['Body'])  # No JSON parsing here

        # Delete the message after processing
        sqs.delete_message(
            QueueUrl=sqs_queue_url,
            ReceiptHandle=message['ReceiptHandle']
        )
        print("✅ Message deleted\n")

    # Optional sleep to avoid tight loop
    time.sleep(1)
