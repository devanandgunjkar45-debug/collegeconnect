from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='core/password_reset.html',
        email_template_name='core/emails/password_reset_email.txt',
        subject_template_name='core/emails/password_reset_subject.txt',
        success_url=reverse_lazy('core:password_reset_done')
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='core/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='core/password_reset_confirm.html',
        success_url=reverse_lazy('core:password_reset_complete')
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='core/password_reset_complete.html'
    ), name='password_reset_complete'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('pending-users/', views.pending_users, name='pending_users'),
    path('pending-users/<int:user_id>/remove/', views.remove_user, name='remove_user'),
    path('pending-registrations/', views.pending_registrations, name='pending_registrations'),
    path('pending-registrations/<int:registration_id>/approve/', views.approve_registration, name='approve_registration'),
    path('pending-registrations/<int:registration_id>/reject/', views.reject_registration, name='reject_registration'),
    path('admin-events/', views.admin_events, name='admin_events'),
    path('admin-events/<int:event_id>/', views.admin_event_detail, name='admin_event_detail'),
    path('admin-events/create/', views.admin_event_create, name='admin_event_create'),
    path('admin-events/<int:event_id>/approve/', views.approve_event, name='approve_event'),
    path('admin-events/<int:event_id>/reject/', views.reject_event, name='reject_event'),
    path('admin-announcements/', views.admin_announcements, name='admin_announcements'),
    path('admin-announcements/create/', views.admin_announcement_create, name='admin_announcement_create'),
    path('admin-announcements/<int:announcement_id>/edit/', views.admin_announcement_edit, name='admin_announcement_edit'),
    path('admin-gallery/', views.admin_gallery, name='admin_gallery'),
    path('admin-gallery/add/', views.admin_gallery_create, name='admin_gallery_create'),
    path('admin-gallery/<int:gallery_id>/edit/', views.admin_gallery_edit, name='admin_gallery_edit'),
    path('admin-gallery/<int:gallery_id>/delete/', views.admin_gallery_delete, name='admin_gallery_delete'),
    path('admin-banners/', views.admin_banners, name='admin_banners'),
    path('admin-banners/add/', views.admin_banner_create, name='admin_banner_create'),
    path('admin-banners/<int:banner_id>/edit/', views.admin_banner_edit, name='admin_banner_edit'),
    path('admin-banners/<int:banner_id>/delete/', views.admin_banner_delete, name='admin_banner_delete'),
    path('admin-participants/', views.admin_participants, name='admin_participants'),
    path('admin-events/<int:event_id>/mark-ongoing/', views.mark_event_ongoing, name='mark_event_ongoing'),
    path('admin-events/<int:event_id>/mark-completed/', views.mark_event_completed, name='mark_event_completed'),
    path('coordinator/dashboard/', views.coordinator_dashboard, name='coordinator_dashboard'),
    path('coordinator/events/create/', views.coordinator_event_create, name='coordinator_event_create'),
    path('coordinator/events/<int:event_id>/edit/', views.coordinator_event_edit, name='coordinator_event_edit'),
    path('profile/', views.profile, name='profile'),
    path('events/', views.event_list, name='event_list'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/<int:event_id>/register/', views.event_register, name='event_register'),
    path('events/<int:event_id>/pay/', views.event_pay, name='event_pay'),
    path('my-events/', views.my_events, name='my_events'),
    path('notifications/', views.notifications, name='notifications'),
    path('announcements/', views.announcements, name='announcements'),
    path('gallery/', views.gallery, name='gallery'),
]
