from django.db import models

# Create your models here.
class Event(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    date = models.DateTimeField()
    description = models.TextField()

    def __str__(self):
        return self.name


class Attendee(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.name


class Ticket(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    attendee = models.ForeignKey(Attendee, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket for {self.attendee.name} to {self.event.name}"