from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('create/', views.event_create, name='event_create'),
    path('update/<int:pk>/', views.event_update, name='event_update'),
    path('delete/<int:pk>/', views.event_delete, name='event_delete'),
    
     # Attendee URLs
    path('attendees/', views.attendee_list, name='attendee_list'),
    path('attendees/create/', views.attendee_create, name='attendee_create'),
    path('attendees/update/<int:pk>/', views.attendee_update, name='attendee_update'),
    path('attendees/delete/<int:pk>/', views.attendee_delete, name='attendee_delete'),

    # Ticket URLs
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/create/', views.ticket_create, name='ticket_create'),
    path('tickets/delete/<int:pk>/', views.ticket_delete, name='ticket_delete'),
]
