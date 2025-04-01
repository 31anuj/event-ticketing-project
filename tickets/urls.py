# tickets/urls.py
from django.urls import path
from . import views
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from .views import signup_view



urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('events/', views.event_list, name='event_list'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/update/<str:event_id>/', views.event_update, name='event_update'),
    path('events/delete/<str:event_id>/', views.event_delete, name='event_delete'),


    # Attendee
    path('attendees/', views.attendee_list, name='attendee_list'),
    path('attendees/create/', views.attendee_create, name='attendee_create'),
    path('attendees/<str:attendee_id>/edit/', views.attendee_update, name='attendee_update'),
    path('attendees/<str:attendee_id>/delete/', views.attendee_delete, name='attendee_delete'),


    # Tickets
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/create/', views.ticket_create, name='ticket_create'),

    # 👇 This is the FIXED delete URL that takes attendee_name and event_name
    path('tickets/delete/<str:ticket_id>/', views.ticket_delete, name='ticket_delete'),
    path('tickets/update/<str:ticket_id>/', views.ticket_update, name='ticket_update'),

    path('events/edit/<str:event_id>/', views.event_update, name='event_update'),
    path('events/update/<str:event_id>/', views.event_update, name='event_update'),
    path('events/delete/<str:event_id>/', views.event_delete, name='event_delete'),

    
    path('', TemplateView.as_view(template_name='tickets/home.html'), name='home'),
     # Auth
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('signup/', signup_view, name='signup'),
    
    
    
    path('attendee-dashboard/', views.attendee_dashboard, name='attendee_dashboard'),
    path('organizer-dashboard/', views.organizer_dashboard, name='organizer_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Authentication
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

]
