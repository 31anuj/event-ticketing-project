'''import boto3
import json
from config import AWS_ACCESS_KEY, AWS_SECRET_KEY, REGION_NAME, SNS_TOPIC_ARN

# Replace with your SNS Topic ARN
TOPIC_ARN = 'arn:aws:sns:eu-west-1:123456789012:TicketBookingTopic'  # 👈 Use your actual ARN

sns_client = boto3.client(
    'sns', 
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name='eu-west-1'
)

def publish_ticket_notification(event_name, attendee_name, attendee_email):
    message = f"🎫 Ticket booked for {event_name} by {attendee_name} ({attendee_email})"
    response = sns_client.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=message,
        Subject="New Ticket Booking Notification"
    )

    return response
    '''
import boto3
from config import REGION_NAME, SNS_TOPIC_ARN

sns_client = boto3.client('sns', region_name=REGION_NAME)

def publish_ticket_notification(message):
    response = sns_client.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=message,
        Subject='New Ticket Booking'
    )
    return response
