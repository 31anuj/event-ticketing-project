import boto3
import uuid
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from .config import DYNAMODB_TABLE_NAME

# Attendees Table Name
ATTENDEE_TABLE_NAME = "Attendees"

# Initialize DynamoDB resource and table
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE_NAME)
attendee_table = dynamodb.Table('Attendees')

def save_ticket_to_dynamodb(event_name, attendee_name, attendee_email):
    """
    Save ticket information to DynamoDB
    """
    try:
        ticket_id = str(uuid.uuid4())  # Unique ID if needed for future enhancements

        table.put_item(
            Item={
                'attendee_name': attendee_name,
                'event_name': event_name,
                'attendee_email': attendee_email,
                'ticket_id': ticket_id  # Optional: not used as key here
            }
        )
        print("✅ Ticket saved to DynamoDB")
    except Exception as e:
        print("❌ DynamoDB Error:", str(e))


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
