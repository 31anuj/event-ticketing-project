from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Create your models here.
class Event(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    date = models.DateTimeField()
    description = models.TextField()
    
    file_url = models.URLField(blank=True, null=True)

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
