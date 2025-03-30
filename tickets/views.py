import uuid
from .config import ticket_table, event_table
from django.shortcuts import render, redirect, get_object_or_404
from .forms import EventForm, AttendeeForm, TicketForm
from .models import Event, Attendee, Ticket
from event_ticketing_lib.s3_utils import upload_file_to_s3
from event_ticketing_lib.sns_utils import publish_ticket_notification
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from event_ticketing_lib.sqs_utils import send_message_to_sqs
from tickets.forms import CustomUserCreationForm
from .models import CustomUser
from .dynamo_utils import delete_ticket_from_dynamodb
from .dynamo_utils import get_event_by_id, update_event_in_dynamodb, delete_event_from_dynamodb
from .config import ticket_table, event_table
from django.http import HttpResponse
from boto3.dynamodb.conditions import Key
from .dynamo_utils import save_event_to_dynamodb, get_all_events_from_dynamodb
from tickets.dynamo_utils import (
    get_all_tickets_from_dynamodb,
    save_ticket_to_dynamodb,
    delete_ticket_from_dynamodb,
    get_all_attendees_from_dynamodb,
    save_attendee_to_dynamodb,
    delete_attendee_from_dynamodb,
    update_attendee_in_dynamodb,
    get_attendee_by_id
)

# ------------------ EVENT VIEWS ------------------
def event_list(request):
    events = get_all_events_from_dynamodb()
    return render(request, 'tickets/event_list.html', {'events': events})




def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event_data = form.cleaned_data
            event_data['event_id'] = str(uuid.uuid4())
            save_event_to_dynamodb(event_data)
            return redirect('event_list')
    else:
        form = EventForm()
    return render(request, 'tickets/event_form.html', {'form': form})


def event_update(request, event_id):
    event = get_event_by_id(event_id)
    if not event:
        return HttpResponse("❌ Event not found", status=404)

    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            updated_data = {
                'name': form.cleaned_data['name'],
                'date': form.cleaned_data['date'].isoformat(),  # Convert to string
                'location': form.cleaned_data['location'],
                'description': form.cleaned_data['description'],
            }
            update_event_in_dynamodb(event_id, updated_data)
            return redirect('event_list')
    else:
        form = EventForm(initial=event)

    return render(request, 'tickets/event_form.html', {
        'form': form,
        'event': event,
    })


def event_delete(request, event_id):
    event = get_event_by_id(event_id)
    if not event:
        return HttpResponse("❌ Event not found", status=404)

    if request.method == 'POST':
        delete_event_from_dynamodb(event_id)
        return redirect('event_list')

    return render(request, 'tickets/event_confirm_delete.html', {'event': event})



# ------------------ ATTENDEE VIEWS ------------------

# List Attendees
def attendee_list(request):
    attendees = get_all_attendees_from_dynamodb()
    return render(request, 'tickets/attendee_list.html', {'attendees': attendees})


# Create Attendee
def attendee_create(request):
    if request.method == 'POST':
        form = AttendeeForm(request.POST)
        if form.is_valid():
            attendee_id = str(uuid.uuid4())
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']

            # Pass individual values instead of a dict
            save_attendee_to_dynamodb(attendee_id, name, email)

            return redirect('attendee_list')
    else:
        form = AttendeeForm()
    return render(request, 'tickets/attendee_form.html', {'form': form})


# Update Attendee
# Update Attendee
def attendee_update(request, attendee_id):
    attendee = get_attendee_by_id(attendee_id)

    if request.method == 'POST':
        form = AttendeeForm(request.POST)
        if form.is_valid():
            updated_data = form.cleaned_data
            updated_data['attendee_id'] = attendee_id  # Preserve the original ID
            update_attendee_in_dynamodb(attendee_id, updated_data)
            return redirect('attendee_list')
    else:
        form = AttendeeForm(initial={
            'name': attendee['name'],
            'email': attendee['email']
        })

    return render(request, 'tickets/attendee_form.html', {'form': form})



# Delete Attendee
def attendee_delete(request, attendee_id):
    if request.method == 'POST':
        delete_attendee_from_dynamodb(attendee_id)
        return redirect('attendee_list')
    attendee = get_attendee_by_id(attendee_id)
    return render(request, 'tickets/attendee_confirm_delete.html', {'attendee': attendee})


# ------------------ TICKET VIEWS (Using DynamoDB) ------------------


def ticket_list(request):
    try:
        response = ticket_table.scan()
        tickets = response.get('Items', [])
        
        # Add event image URL to each ticket
        for ticket in tickets:
            try:
                event_id = ticket.get('event_id')  # Safely get event_id
                if not event_id:
                    ticket['event_image_url'] = None
                    continue

                event_response = event_table.get_item(Key={'event_id': event_id})
                event = event_response.get('Item')
                ticket['event_image_url'] = event.get('file') if event else None
            except Exception as e:
                ticket['event_image_url'] = None
    except Exception as e:
        print("Error fetching tickets:", e)
        tickets = []

    return render(request, 'tickets/ticket_list.html', {'tickets': tickets})



def ticket_create(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save()

            # Prepare message for SQS
            message = f"Ticket booked for event: {ticket.event.name}, by attendee: {ticket.attendee.name}"

            try:
                send_message_to_sqs(message)
                print("✅ SQS message sent")
            except Exception as e:
                print("❌ SQS Error:", str(e))

            try:
                # Save to DynamoDB
                save_ticket_to_dynamodb(
                    ticket_id=str(ticket.id),  # Use ticket.id from SQLite
                    event_name=ticket.event.name,
                    attendee_name=ticket.attendee.name,
                    attendee_email=ticket.attendee.email
                )
                print("✅ Ticket saved to DynamoDB")
            except Exception as e:
                print("❌ DynamoDB Error:", str(e))

            try:
                # SNS notification
                sns_message = f"Ticket booked for event: {ticket.event.name}, by attendee: {ticket.attendee.name} ({ticket.attendee.email})"
                publish_ticket_notification(sns_message)
                print("✅ SNS notification sent")
            except Exception as e:
                print("❌ SNS Error:", str(e))

            return redirect('ticket_list')
    else:
        form = TicketForm()

    return render(request, 'tickets/ticket_form.html', {'form': form})




def ticket_delete(request, ticket_id):
    try:
        ticket_table.delete_item(Key={'ticket_id': ticket_id})
    except Exception as e:
        print(f"Error deleting ticket {ticket_id}: {e}")
    return redirect('ticket_list')
    
def ticket_update(request, ticket_id):
    # Get existing ticket from DynamoDB
    response = ticket_table.get_item(Key={'ticket_id': ticket_id})
    ticket_data = response.get('Item')

    if not ticket_data:
        return render(request, 'error.html', {'message': 'Ticket not found'})

    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            updated_data = form.cleaned_data
            # Update the ticket in DynamoDB
            ticket_table.put_item(Item={
                'ticket_id': ticket_id,
                'attendee_name': updated_data['attendee_name'],
                'event_id': updated_data['event_id'],
                'booking_date': updated_data['booking_date'].isoformat()
            })
            return redirect('ticket_list')
    else:
        # Pre-fill form with existing data
        form = TicketForm(initial={
            'attendee_name': ticket_data.get('attendee_name'),
            'event_id': ticket_data.get('event_id'),
            'booking_date': ticket_data.get('booking_date')
        })

    return render(request, 'tickets/ticket_form.html', {'form': form, 'ticket_id': ticket_id})

# User Signup
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            print("User role:", user.role)
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'organizer':
                return redirect('organizer_dashboard')
            else:
                return redirect('attendee_dashboard')
    else:
        form = CustomUserCreationForm()
    
    # ✅ Add this return so the form loads properly on GET
    return render(request, 'registration/signup.html', {'form': form})
    
    



# User Login
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'registration/login.html')
    
# User Logout
def logout_view(request):
    logout(request)
    return redirect('login')
    
'''    
@login_required
def attendee_dashboard(request):
    return render(request, 'tickets/attendee_dashboard.html')

@login_required
def organizer_dashboard(request):
    return render(request, 'tickets/organizer_dashboard.html')

@login_required
def admin_dashboard(request):
    return render(request, 'tickets/admin_dashboard.html')
'''    
    
def admin_dashboard(request):
    return HttpResponse("Welcome Admin!")

def organizer_dashboard(request):
    return HttpResponse("Welcome Organizer!")

def attendee_dashboard(request):
    return HttpResponse("Welcome Attendee!")
    
# Dashboard Redirect
@login_required
def dashboard_view(request):
    user = request.user
    if user.role == 'admin':
        return redirect('admin_dashboard')
    elif user.role == 'organizer':
        return redirect('organizer_dashboard')
    elif user.role == 'attendee':
        return redirect('attendee_dashboard')
    else:
        return HttpResponse("❌ Role not recognized", status=403)