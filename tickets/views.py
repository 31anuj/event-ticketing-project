import uuid
import boto3
from .config import sqs_queue_url
from .config import ticket_table, event_table, sqs_queue_url, AWS_STORAGE_BUCKET_NAME
from django.shortcuts import render, redirect, get_object_or_404
from .forms import EventForm, AttendeeForm, TicketForm
from .forms import TicketForm
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

import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import base64
import json
from django.conf import settings
from .config import s3_bucket_name
from django.core.files.storage import default_storage
sqs = boto3.client('sqs')


# ------------------ EVENT VIEWS ------------------
def event_list(request):
    events = get_all_events_from_dynamodb()
    return render(request, 'tickets/event_list.html', {'events': events})


def upload_file_to_s3(file_obj, filename):
    s3 = boto3.client('s3')
    s3.upload_fileobj(file_obj, AWS_STORAGE_BUCKET_NAME, filename)
    return f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{filename}"


def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            print(form.cleaned_data)
            image_url = form.cleaned_data.get('banner_url', '')

            uploaded_file = request.FILES.get('file')
            if uploaded_file:
                filename = f"event-banners/{uuid.uuid4()}.jpg"
                image_url = upload_file_to_s3(uploaded_file, filename)

            event_id = str(uuid.uuid4())
            event_table.put_item(Item={
                'event_id': event_id,
                'name': form.cleaned_data['event_name'],
                'description': form.cleaned_data['description'],
                'location': form.cleaned_data['location'],
                'date': form.cleaned_data['date'].isoformat(),
                'banner_url': image_url,
            })
            return redirect('event_list')
    else:
        form = EventForm()

    return render(request, 'tickets/event_form.html', {'form': form})

def event_update(request, event_id):
    event = get_event_by_id(event_id)
    if not event:
        return HttpResponse("❌ Event not found", status=404)

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)  # ✅ Include request.FILES
        if form.is_valid():
            print(form.cleaned_data)
            updated_data = {
                'event_id': event_id,
                'name': form.cleaned_data.get('event_name', event.get('name')),
                'description': form.cleaned_data['description'],
                'date': form.cleaned_data['date'].isoformat(),
                'location': form.cleaned_data['location'],
            }

            # ✅ Handle file upload if user selected a new file
            if request.FILES.get('event_image_file'):
                file = request.FILES['event_image_file']
                s3 = boto3.client('s3')
                file_key = f"event-banners/{uuid.uuid4()}_{file.name}"
                s3.upload_fileobj(file, AWS_STORAGE_BUCKET_NAME, file_key)
                image_url = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{file_key}"
                updated_data['banner_url'] = image_url

            # ✅ If no new file uploaded, check if they provided an image URL
            elif form.cleaned_data.get('event_image_url'):
                updated_data['banner_url'] = form.cleaned_data['event_image_url']

            # ✅ If neither file nor URL, fallback to existing image
            else:
                updated_data['banner_url'] = event.get('banner_url', '')

            # Save to DynamoDB
            event_table.put_item(Item=updated_data)
            return redirect('event_list')
    else:
        form = EventForm(initial={
            'event_name': event.get('event_name'),
            'description': event.get('description'),
            'date': event.get('date'),
            'location': event.get('location'),
            'event_image_url': event.get('banner_url'),
        })

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
    response = ticket_table.scan()
    tickets = response['Items']

    # For each ticket, get the corresponding event image URL from the Events table
    for ticket in tickets:
        try:
            event_id = ticket.get('event_id')
            event_response = event_table.get_item(Key={'event_id': event_id})
            event = event_response.get('Item')
            ticket['event_image_url'] = event.get('file') if event else None
        except KeyError:
            ticket['event_image_url'] = None

    return render(request, 'tickets/ticket_list.html', {'tickets': tickets})



'''def ticket_create(request):
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

    return render(request, 'tickets/ticket_form.html', {'form': form})'''
    
def ticket_create(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            ticket_id = str(uuid.uuid4())

            # ✅ Get event details using event_id
            event = get_event_by_id(data['event_id'])

            if not event:
                return HttpResponse("❌ Invalid Event ID. Event not found.", status=400)

            event_name = event.get('name', 'Unknown Event')

            # ✅ Generate QR Code
            qr_data = f"Ticket ID: {ticket_id}, Event: {event_name}, Attendee: {data['attendee_name']}"
            qr_img = qrcode.make(qr_data)

            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            qr_bytes = buffer.getvalue()

            # ✅ Upload QR Code to S3
            qr_key = f"tickets/qrcodes/{ticket_id}.png"
            s3= boto3.client('s3')
            s3.put_object(Bucket=AWS_STORAGE_BUCKET_NAME, Key=qr_key, Body=qr_bytes, ContentType='image/png')
            qr_url = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{qr_key}"

            # ✅ Save ticket to DynamoDB
            ticket_table.put_item(Item={
                'ticket_id': ticket_id,
                'attendee_name': data['attendee_name'],
                'event_id': data['event_id'],
                'booking_date': data['booking_date'].isoformat(),
                'qr_code_url': qr_url
            })

            # ✅ Send SQS message
            message_body = f"Ticket booked for event: {event_name}, by attendee: {data['attendee_name']}"
            sqs.send_message(QueueUrl=sqs_queue_url, MessageBody=message_body)

            return redirect('ticket_list')
    else:
        form = TicketForm()

    return render(request, 'tickets/ticket_form.html', {'form': form})






# Ticket Delete View
def ticket_delete(request, ticket_id):
    try:
        # Delete the ticket from DynamoDB
        ticket_table.delete_item(Key={'ticket_id': ticket_id})
    except Exception as e:
        print(f"Error deleting ticket: {e}")

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
        

def update_event_in_dynamodb(event_id, updated_data):
    event_table.update_item(
        Key={'event_id': event_id},
        UpdateExpression="SET #n = :name, #d = :date, #l = :location, #desc = :desc, #b = :banner",
        ExpressionAttributeNames={
            '#n': 'name',
            '#d': 'date',
            '#l': 'location',
            '#desc': 'description',
            '#b': 'banner_url',
        },
        ExpressionAttributeValues={
            ':name': updated_data['name'],
            ':date': updated_data['date'],
            ':location': updated_data['location'],
            ':desc': updated_data['description'],
            ':banner': updated_data['banner_url'],
        }
    )

def get_event_by_id(event_id):
    response = event_table.get_item(Key={'event_id': event_id})
    return response.get('Item')
