# tickets/config.py
import boto3

dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
event_table = dynamodb.Table('Events')  # Make sure this matches your actual table name
attendee_table = dynamodb.Table('Attendees')
ticket_table = dynamodb.Table('Tickets')
DYNAMODB_TABLE_NAME = 'TicketBookings'
