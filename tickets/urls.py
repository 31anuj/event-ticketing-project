# tickets/urls.py
from django.urls import path
from . import views
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from .views import signup_view



urlpatterns = [
    #path('', views.event_list, name='event_list'),
    path('events/', views.event_list, name='event_list'),
    path('events_create/', views.event_create, name='event_create'),
    path('events_update/<str:event_id>/', views.event_update, name='event_update'),
    path('events_delete/<str:event_id>/', views.event_delete, name='event_delete'),


    # Attendee
    path('attendees/', views.attendee_list, name='attendee_list'),
    path('attendees_create/', views.attendee_create, name='attendee_create'),
    path('attendees/<str:attendee_id>/edit/', views.attendee_update, name='attendee_update'),
    path('attendees/<str:attendee_id>/delete/', views.attendee_delete, name='attendee_delete'),


    # Tickets
    path('tickets_list/', views.ticket_list, name='ticket_list'),
    path('tickets_create/', views.ticket_create, name='ticket_create'),

    # 👇 This is the FIXED delete URL that takes attendee_name and event_name
    path('tickets_delete/<str:ticket_id>/', views.ticket_delete, name='ticket_delete'),
    path('tickets_update/<str:ticket_id>/', views.ticket_update, name='ticket_update'),

    path('events_edit/<str:event_id>/', views.event_update, name='event_update'),
    path('events_update/<str:event_id>/', views.event_update, name='event_update'),
    path('events_delete/<str:event_id>/', views.event_delete, name='event_delete'),

    
    path('', TemplateView.as_view(template_name='tickets/home.html'), name='home'),
     # Auth
    
    
    path('attendee_dashboard/', views.attendee_dashboard, name='attendee_dashboard'),
    path('organizer_dashboard/', views.organizer_dashboard, name='organizer_dashboard'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    # Authentication
    
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

]


