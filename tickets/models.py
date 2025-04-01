from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Create your models here.
# tickets/models.py

class Event(models.Model):
    event_name = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()
    banner = models.FileField(upload_to='event_banners/', blank=True, null=True)

    def __str__(self):
        return self.event_name


class Attendee(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.name



class Ticket(models.Model):
    ticket_id = models.CharField(max_length=100, primary_key=True)
    attendee_name = models.CharField(max_length=100)
    event_id = models.CharField(max_length=100)
    booking_date = models.DateField()

    def __str__(self):
        return f"Ticket for {self.attendee.name} to {self.event.name}"
        
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('Organizer', 'Organizer'),
        ('Attendee', 'Attendee'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Attendee')

    def __str__(self):
        return self.username
