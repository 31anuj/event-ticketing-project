from django.shortcuts import render, redirect, get_object_or_404
from .forms import EventForm, AttendeeForm, TicketForm
from .models import Event, Attendee, Ticket
from event_ticketing_lib.dynamodb_utils import save_ticket_to_dynamodb

# List all events
def event_list(request):
    events = Event.objects.all()
    return render(request, 'tickets/event_list.html', {'events': events})

# Create new event
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('event_list')
    else:
        form = EventForm()
    return render(request, 'tickets/event_form.html', {'form': form})

# Update event
def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_list')
    else:
        form = EventForm(instance=event)
    return render(request, 'tickets/event_form.html', {'form': form})

# Delete event
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
        return redirect('event_list')
    return render(request, 'tickets/event_confirm_delete.html', {'event': event})
    
def attendee_create(request):
    if request.method == 'POST':
        form = AttendeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('attendee_list')
    else:
        form = AttendeeForm()
    return render(request, 'tickets/attendee_form.html', {'form': form})

    
def attendee_list(request):
    attendees = Attendee.objects.all()
    return render(request, 'tickets/attendee_list.html', {'attendees': attendees})
    
def attendee_update(request, pk):
    attendee = get_object_or_404(Attendee, pk=pk)
    if request.method == 'POST':
        form = AttendeeForm(request.POST, instance=attendee)
        if form.is_valid():
            form.save()
            return redirect('attendee_list')
    else:
        form = AttendeeForm(instance=attendee)
    return render(request, 'tickets/attendee_form.html', {'form': form})
    
def attendee_delete(request, pk):
    attendee = get_object_or_404(Attendee, pk=pk)
    if request.method == 'POST':
        attendee.delete()
        return redirect('attendee_list')
    return render(request, 'tickets/attendee_confirm_delete.html', {'attendee': attendee})

def ticket_list(request):
    tickets = Ticket.objects.select_related('event', 'attendee')
    return render(request, 'tickets/ticket_list.html', {'tickets': tickets})

def ticket_create(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save()  # Save to Django DB

            # Save to DynamoDB
            save_ticket_to_dynamodb(
                event_name=ticket.event.name,
                attendee_name=ticket.attendee.name,
                attendee_email=ticket.attendee.email,
            )

            return redirect('ticket_list')
    else:
        form = TicketForm()
    return render(request, 'tickets/ticket_form.html', {'form': form})

def ticket_delete(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == 'POST':
        ticket.delete()
        return redirect('ticket_list')
    return render(request, 'tickets/ticket_confirm_delete.html', {'ticket': ticket})

