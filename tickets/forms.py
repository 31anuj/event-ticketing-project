from django import forms
from .models import Event, Attendee, Ticket
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CustomUser

class EventForm(forms.ModelForm):
    file = forms.FileField(required=False)
    
    class Meta:
        model = Event
        fields = ['name', 'location', 'date', 'description', 'file']
        
class AttendeeForm(forms.ModelForm):
    class Meta:
        model = Attendee
        fields = ['name', 'email']

class TicketForm(forms.Form):
    attendee_name = forms.CharField(max_length=100)
    event_id = forms.CharField(max_length=100)
    booking_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

        
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