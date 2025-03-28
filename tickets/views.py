import uuid
from django.shortcuts import render, redirect, get_object_or_404
from .forms import EventForm, AttendeeForm, TicketForm
from .models import Event, Attendee, Ticket
from event_ticketing_lib.s3_utils import upload_file_to_s3
from event_ticketing_lib.sns_utils import publish_ticket_notification
from event_ticketing_lib.sqs_utils import send_message_to_sqs
from .dynamo_utils import delete_ticket_from_dynamodb
from .dynamo_utils import get_event_by_id, update_event_in_dynamodb
from django.http import HttpResponse
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


def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
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
        tickets = get_all_tickets_from_dynamodb()
    except Exception as e:
        print("❌ DynamoDB Scan Error:", str(e))
        tickets = []
    return render(request, 'tickets/ticket_list.html', {'tickets': tickets})


def ticket_create(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save()
            message = f"Ticket booked for event: {ticket.event.name}, by attendee: {ticket.attendee.name}"

            try:
                send_message_to_sqs(message)
                print("✅ SQS message sent")
            except Exception as e:
                print("❌ SQS Error:", str(e))

            try:
                save_ticket_to_dynamodb(
                    event_name=ticket.event.name,
                    attendee_name=ticket.attendee.name,
                    attendee_email=ticket.attendee.email
                )
                print("✅ Ticket saved to DynamoDB")
            except Exception as e:
                print("❌ DynamoDB Error:", str(e))

            try:
                sns_message = f"Ticket booked for event: {ticket.event.name}, by attendee: {ticket.attendee.name} ({ticket.attendee.email})"
                publish_ticket_notification(sns_message)
                print("✅ SNS notification sent")
            except Exception as e:
                print("❌ SNS Error:", str(e))

            return redirect('ticket_list')
    else:
        form = TicketForm()
    return render(request, 'tickets/ticket_form.html', {'form': form})


def ticket_delete(request, attendee_name, event_name):
    if request.method == 'POST':
        try:
            delete_ticket_from_dynamodb(attendee_name, event_name)
            print("✅ Ticket deleted from DynamoDB")
        except Exception as e:
            print("❌ DynamoDB Delete Error:", str(e))
        return redirect('ticket_list')

    return render(request, 'tickets/ticket_confirm_delete.html', {
        'attendee_name': attendee_name,
        'event_name': event_name
    })