from django import forms
from .models import Event, Attendee, Ticket
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CustomUser
from .dynamo_utils import get_all_events_from_dynamodb

class EventForm(forms.Form):
    event_name = forms.CharField(label='Event Name')
    description = forms.CharField(widget=forms.Textarea)
    date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    location = forms.CharField(max_length=255)
    event_image_url = forms.URLField(required=False, label='Event Image (URL or upload)')
    event_image_file = forms.FileField(required=False)
    banner_url = forms.URLField(required=False)
    
    class Meta:
        model = Event
        fields = ['event_name', 'description', 'location', 'date', 'banner_url']
        
class AttendeeForm(forms.ModelForm):
    class Meta:
        model = Attendee
        fields = ['name', 'email']

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['attendee_name', 'event_id', 'booking_date']

        
def attendee_list(request):
    attendees = Attendee.objects.all()
    return render(request, 'tickets/attendee_list.html', {'attendees': attendees})

def attendee_create(request):
    if request.method == 'POST':
        form = AttendeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('attendee_list')
    else:
        form = AttendeeForm()
    return render(request, 'tickets/attendee_form.html', {'form': form})

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

# ---------- Ticket Views ----------

def ticket_list(request):
    tickets = Ticket.objects.select_related('event', 'attendee')
    return render(request, 'tickets/ticket_list.html', {'tickets': tickets})

def ticket_create(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            form.save()
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
    
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'role']
        
class TicketForm(forms.Form):
    attendee_name = forms.CharField(max_length=100)
    event_id = forms.ChoiceField(choices=[])  # Will fill dynamically
    booking_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        events = get_all_events_from_dynamodb()
        choices = [(event['event_id'], event.get('name', 'Unnamed')) for event in events]
        self.fields['event_id'].choices = choices