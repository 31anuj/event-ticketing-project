# tickets/config.py
import boto3

sqs_queue_url = 'https://sqs.eu-west-1.amazonaws.com/250738637992/ticket-queue' 
s3_bucket_name = 'event-ticketing-media-anuj-9821'
dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
event_table = dynamodb.Table('Events')  # Make sure this matches your actual table name
attendee_table = dynamodb.Table('Attendees')
ticket_table = dynamodb.Table('Tickets')
DYNAMODB_TABLE_NAME = 'TicketBookings'
AWS_STORAGE_BUCKET_NAME = 'event-ticketing-media-anuj-9821'



