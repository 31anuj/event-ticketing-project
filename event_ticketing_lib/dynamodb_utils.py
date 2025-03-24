import boto3
import uuid
from datetime import datetime

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

# Connect to the table
table = dynamodb.Table('TicketBookings')

def save_ticket_to_dynamodb(event_name, attendee_name, attendee_email):
    ticket_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()

    item = {
        'ticket_id': ticket_id,
        'event_name': event_name,
        'attendee_name': attendee_name,
        'attendee_email': attendee_email,
        'booking_date': timestamp,
    }

    table.put_item(Item=item)
    return ticket_id
