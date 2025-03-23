from django.shortcuts import render, redirect, get_object_or_404
from .models import Event
from .forms import EventForm

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
