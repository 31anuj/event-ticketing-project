import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
import logging
from datetime import datetime

AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

dynamodb = boto3.resource(
    'dynamodb',
    region_name=AWS_REGION
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize DynamoDB resource
dynamodb_client = boto3.resource('dynamodb')

class DynamoDBManager:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.tables = {
            'Events': None,
            'Attendees': None,
            'Tickets': None
        }
        self._initialize_tables()
    
    def _initialize_tables(self):
        """Initialize tables with fallback behavior"""
        for table_name in self.tables.keys():
            try:
                self.tables[table_name] = self.dynamodb.Table(table_name)
                # Test connection with a simple operation
                self.tables[table_name].table_status
                logger.info(f"Successfully connected to {table_name} table")
            except ClientError as e:
                logger.warning(f"Could not access {table_name} table: {str(e)}")
                self.tables[table_name] = None

    # ========== EVENT OPERATIONS ==========
    def get_all_events(self):
        """Get all events with fallback to sample data"""
        fallback_events = [{
            'event_id': 'sample1',
            'name': 'Sample Event',
            'date': datetime.now().isoformat(),
            'location': 'Virtual',
            'description': 'Fallback event data'
        }]
        
        if not self.tables['Events']:
            logger.warning("No access to Events table - returning sample data")
            return fallback_events
            
        try:
            response = self.tables['Events'].scan(
                Select='SPECIFIC_ATTRIBUTES',
                ProjectionExpression='event_id, #n, #d, location, description',
                ExpressionAttributeNames={'#n': 'name', '#d': 'date'}
            )
            return response.get('Items', fallback_events)
        except ClientError as e:
            logger.error(f"Error fetching events: {str(e)}")
            return fallback_events

    def get_event_by_id(self, event_id):
        try:
            table = dynamodb_client.Table('Events')
            response = table.scan(
                    Limit=100
                )
            
            # response = dynamodb_client.get_item(
            #     TableName='Events',
            #     Key={
            #         'event_id': {'S': event_id}
            #     }
            # )
            return response.get('Item')
        except ClientError as e:
            print(f"Error fetching event with ID {event_id}: {e}")
            return None

    # ========== TICKET OPERATIONS ==========
    def get_all_tickets(self):
        """Get all tickets with fallback to empty list"""
        if not self.tables['Tickets']:
            logger.warning("No access to Tickets table - returning empty list")
            return []
            
        try:
            response = self.tables['Tickets'].scan(
                Limit=10,  # Reduce request size
                Select='SPECIFIC_ATTRIBUTES',
                ProjectionExpression='ticket_id,event_id,attendee_id'
            )
            return response.get('Items', [])
        except ClientError as e:
            if e.response['Error']['Code'] == 'AccessDeniedException':
                logger.warning("Permission denied for scan operation - returning empty list")
                return []
            logger.error(f"Error fetching tickets: {str(e)}")
            return []

    def create_ticket(self, ticket_data):
        """Create ticket with fallback"""
        if not self.tables['Tickets']:
            logger.warning("No access to Tickets table - cannot create ticket")
            return False
            
        try:
            self.tables['Tickets'].put_item(Item=ticket_data)
            return True
        except ClientError as e:
            logger.error(f"Error creating ticket: {str(e)}")
            return False

    def delete_ticket(self, ticket_id):
        """Delete ticket with fallback"""
        if not self.tables['Tickets']:
            logger.warning("No access to Tickets table - cannot delete ticket")
            return False
            
        try:
            self.tables['Tickets'].delete_item(Key={'ticket_id': ticket_id})
            return True
        except ClientError as e:
            logger.error(f"Error deleting ticket: {str(e)}")
            return False
            
    def get_all_attendees(self):
        """Get all attendees with pagination support"""
        if not self.tables['Attendees']:
            logger.warning("No access to Attendees table")
            return []
            
        try:
            attendees = []
            response = self.tables['Attendees'].scan()
            attendees.extend(response.get('Items', []))
            
            while 'LastEvaluatedKey' in response:
                response = self.tables['Attendees'].scan(
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                attendees.extend(response.get('Items', []))
                
            return attendees
            
        except ClientError as e:
            logger.error(f"Error fetching attendees: {e}")
            return []
    
    def save_attendee(self, attendee_data):
        """Create attendee with fallback"""
        if not self.tables['Attendees']:
            logger.warning("No access to Attendee table - cannot create attendee")
            return False
            
        try:
            self.tables['Attendees'].put_item(Item=attendee_data)
            return True
        except ClientError as e:
            logger.error(f"Error creating attendee: {str(e)}")
            return False
            
    def get_attendee_by_id(self, attendee_id):
        try:
            table = dynamodb_client.Table('Attendees')
            response = table.scan(
                    FilterExpression=Key('attendee_id').eq(attendee_id)
                )
            return response.get('Items', [0])
        except ClientError as e:
            print(f"Error fetching event with ID {attendee_id}: {e}")
            return None
            
    def update_attendee(self, attendee_data):
        try:
            table = dynamodb_client.Table('Attendees')
            response = table.update_item(
                    Key={'attendee_id': attendee_data['attendee_id']},
                    UpdateExpression={
                        'email': attendee_data['email'],
                        'name': attendee_data['name']
                    }
                )

        except ClientError as e:
            print(f"Error fetching event with ID {attendee_data}: {e}")
            return None

# Initialize single instance
db_manager = DynamoDBManager()

# ========== PUBLIC API ==========
# Event functions
def get_all_events_from_dynamodb():
    return db_manager.get_all_events()

def get_event_by_id_from_dynamodb(event_id):
    return db_manager.get_event_by_id(event_id)

# Ticket functions
def get_all_tickets_from_dynamodb():
    return db_manager.get_all_tickets()

def save_ticket_to_dynamodb(ticket_data):
    return db_manager.create_ticket(ticket_data)

def delete_ticket_from_dynamodb(ticket_id):
    return db_manager.delete_ticket(ticket_id)

# Attendee functions
def get_all_attendees_from_dynamodb():
    return db_manager.get_all_attendees()
    
def save_attendee_to_dynamodb(attendee_data):
    return db_manager.save_attendee(attendee_data)
    
def get_attendee_id_from_dynamodb(attendee_id) : 
    return db_manager.get_attendee_by_id(attendee_id)

def update_attendee_in_dynamodb(attendee_data):
    return db_manager.update_attendee(attendee_data)