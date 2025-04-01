import boto3
import uuid
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from .config import DYNAMODB_TABLE_NAME
from .config import event_table


# Attendees Table Name
ATTENDEE_TABLE_NAME = "Attendees"

# Initialize DynamoDB resource and table
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE_NAME)
attendee_table = dynamodb.Table('Attendees')
tickets_table = dynamodb.Table('Tickets')  # if not already declared


def save_ticket_to_dynamodb(ticket_id, event_name, attendee_name, attendee_email):
    try:
        ticket_table.put_item(
            Item={
                'ticket_id': str(ticket_id),
                'event_name': event_name,
                'attendee_name': attendee_name,
                'attendee_email': attendee_email,
            }
        )
    except Exception as e:
        print("❌ Error saving ticket to DynamoDB:", str(e))



def get_all_tickets_from_dynamodb():
    """
    Retrieve all tickets from DynamoDB
    """
    try:
        response = table.scan()
        return response.get("Items", [])
    except Exception as e:
        print("❌ DynamoDB Scan Error:", str(e))
        return []


def delete_ticket_from_dynamodb(attendee_name, event_name):
    """
    Delete a specific ticket from DynamoDB using composite key
    """
    try:
        table.delete_item(
            Key={
                'attendee_name': attendee_name,
                'event_name': event_name
            }
        )
        print("🗑️ Ticket deleted from DynamoDB")
    except Exception as e:
        print("❌ DynamoDB Delete Error:", str(e))

# Save a new attendee
def save_attendee_to_dynamodb(attendee_id, name, email):
    table = dynamodb.Table('Attendees')
    try:
        table.put_item(
            Item={
                'attendee_id': attendee_id,
                'name': name,
                'email': email
            }
        )
        return attendee_id
    except ClientError as e:
        print("Error saving attendee to DynamoDB:", e)
        return None

# Get all attendees
def get_all_attendees_from_dynamodb():
    try:
        response = attendee_table.scan()
        items = response.get("Items", [])
        attendees = []

        for item in items:
            attendees.append({
                'attendee_id': item['attendee_id'],  # removed ['S']
                'name': item['name'],
                'email': item['email'],
            })

        return attendees
    except ClientError as e:
        print("❌ Error fetching attendees:", e)
        return []


# Delete an attendee
def delete_attendee_from_dynamodb(attendee_id):
    try:
        attendee_table.delete_item(
            Key={'attendee_id': attendee_id}  # Make sure the key name matches your table's partition key
        )
        return True
    except ClientError as e:
        print("❌ Error deleting attendee:", e)
        return False
        
# Get a single attendee by ID
def get_attendee_by_id(attendee_id):
    try:
        response = attendee_table.get_item(
            Key={'attendee_id': attendee_id}
        )
        return response.get('Item')
    except ClientError as e:
        print("❌ Error fetching attendee:", e)
        return None

# Update Attendee
# Update Attendee
def update_attendee_in_dynamodb(attendee_id, updated_data):
    try:
        attendee_table.update_item(
            Key={'attendee_id': attendee_id},
            UpdateExpression="SET #n = :name, email = :email",
            ExpressionAttributeNames={'#n': 'name'},
            ExpressionAttributeValues={
                ':name': updated_data['name'],
                ':email': updated_data['email'],
            }
        )
        print("✅ Attendee updated successfully")
        return True
    except ClientError as e:
        print("❌ Error updating attendee:", e)
        return False

# dynamo_utils.py

# Event DynamoDB Table
EVENTS_TABLE_NAME = "Events"
events_table = dynamodb.Table(EVENTS_TABLE_NAME)

def save_event_to_dynamodb(event_data):
    # Convert datetime object to ISO string
    event_data['date'] = event_data['date'].isoformat()

    try:
        events_table.put_item(Item=event_data)
        print("✅ Event saved to DynamoDB.")
    except ClientError as e:
        print("❌ Error saving event to DynamoDB:", e)


def get_all_events_from_dynamodb():
    response = event_table.scan()
    items = response.get('Items', [])
    events = []

    for item in items:
        # Safe fallback extraction
        event = {
    'event_id': item.get('event_id') or item.get('id'),
    'name': item.get('name', '[No Name]'),
    'description': item.get('description', ''),
    'location': item.get('location', ''),
    'date': item.get('date', ''),
    'banner_url': item.get('banner_url', ''),
}
        events.append(event)

    return events

# dynamo_utils.py

# ✅ Step 1: Get Event by ID
def get_event_by_id(event_id):
    try:
        print("🟡 Scanning for event_id:", event_id)
        response = events_table.get_item(Key={'event_id': event_id})
        item = response.get('Item')
        if item:
            print("✅ Event found:", item)
            return {
                'event_id': item['event_id'],
                'name': item['name'],
                'date': item['date'],
                'location': item['location'],
                'description': item['description'],
            }
        print("❌ Event not found")
        return None
    except ClientError as e:
        print("🚨 Error fetching event:", e)
        return None

# ✅ Step 2: Update Event in DynamoDB
def update_event_in_dynamodb(event_id, data):
    try:
        response = events_table.update_item(
            Key={'event_id': event_id},
            UpdateExpression="SET #n = :name, #d = :date, #l = :location, #desc = :description",
            ExpressionAttributeNames={
                '#n': 'name',
                '#d': 'date',
                '#l': 'location',
                '#desc': 'description'
            },
            ExpressionAttributeValues={
                ':name': data['name'],
                ':date': data['date'],
                ':location': data['location'],
                ':description': data['description'],
            }
        )
        print("✅ Event updated:", event_id)
        return True
    except ClientError as e:
        print("❌ Error updating event:", e)
        return False

# ✅ Delete event from DynamoDB
def delete_event_from_dynamodb(event_id):
    try:
        events_table.delete_item(Key={'event_id': event_id})
        print("🗑️ Event deleted:", event_id)
        return True
    except ClientError as e:
        print("❌ Error deleting event:", e)
        return False

# ✅ Save a new ticket to DynamoDB
def save_ticket_to_dynamodb(ticket_data):
    try:
        tickets_table.put_item(Item=ticket_data)
        print("✅ Ticket saved to DynamoDB:", ticket_data)
        return True
    except ClientError as e:
        print("❌ Error saving ticket:", e)
        return False
