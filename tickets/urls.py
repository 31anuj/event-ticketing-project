# tickets/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('create/', views.event_create, name='event_create'),
    path('events/<str:event_id>/edit/', views.event_update, name='event_update'),
    path('events/<str:event_id>/delete/', views.event_delete, name='event_delete'),


    # Attendee
    path('attendees/', views.attendee_list, name='attendee_list'),
    path('attendees/create/', views.attendee_create, name='attendee_create'),
    path('attendees/<str:attendee_id>/edit/', views.attendee_update, name='attendee_update'),
    path('attendees/<str:attendee_id>/delete/', views.attendee_delete, name='attendee_delete'),


    # Tickets
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/create/', views.ticket_create, name='ticket_create'),

    # 👇 This is the FIXED delete URL that takes attendee_name and event_name
    path('tickets/delete/<str:attendee_name>/<str:event_name>/', views.ticket_delete, name='ticket_delete'),
]
