import io
import qrcode
from decimal import Decimal
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core import signing
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils import timezone
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas

from .forms import UserRegisterForm, UserLoginForm, ProfileForm, ContactForm, AnnouncementForm, EventRegistrationForm, FeedbackForm, EventForm, CoordinatorEventForm, EventApprovalForm, GalleryItemForm, BannerForm
from .models import Club, Event, GalleryItem, Banner, Registration, Attendance, Notification, Announcement

User = get_user_model()


def home(request):
    featured_events = Event.objects.filter(status='approved').order_by('date')[:6]
    upcoming = Event.objects.filter(status='approved', date__gte=timezone.now().date())[:3]
    announcements = Announcement.objects.order_by('-publish_date')[:3]
    gallery_items = GalleryItem.objects.order_by('-created_at')[:6]
    banners = Banner.objects.filter(is_active=True).order_by('order', '-created_at')[:3]
    total_events = Event.objects.filter(status='approved').count()
    total_clubs = Club.objects.count()
    upcoming_count = upcoming.count()
    student_registrations = 0
    if request.user.is_authenticated and request.user.is_student:
        student_registrations = Registration.objects.filter(student=request.user).count()
    context = {
        'featured_events': featured_events,
        'upcoming_events': upcoming,
        'announcements': announcements,
        'gallery_items': gallery_items,
        'banners': banners,
        'total_events': total_events,
        'total_clubs': total_clubs,
        'upcoming_count': upcoming_count,
        'student_registrations': student_registrations,
    }
    return render(request, 'core/home.html', context)


def about(request):
    return render(request, 'core/about.html')


def gallery(request):
    items = GalleryItem.objects.order_by('-created_at')[:12]
    return render(request, 'core/gallery.html', {'gallery_items': items})


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = f"CampusConnect contact: {form.cleaned_data['subject']}"
            body = render_to_string('emails/contact_message.txt', {
                'name': form.cleaned_data['name'],
                'email': form.cleaned_data['email'],
                'subject': form.cleaned_data['subject'],
                'message': form.cleaned_data['message'],
            })
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
            admin_user = User.objects.filter(role='admin', is_active=True).first()
            if admin_user:
                Notification.objects.create(
                    user=admin_user,
                    title='New contact request',
                    message=f'{form.cleaned_data["name"]} submitted a contact request: {form.cleaned_data["subject"]}',
                )
            messages.success(request, 'Thank you for reaching out. We will get back to you soon.')
            return redirect('core:contact')
    else:
        form = ContactForm()
    return render(request, 'core/contact.html', {'form': form})


def faq(request):
    return render(request, 'core/faq.html')


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            messages.error(request, 'Administrator access required.')
            return redirect('core:login')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def admin_announcements(request):
    announcements = Announcement.objects.order_by('-publish_date')
    return render(request, 'core/admin_announcements.html', {'announcements': announcements})


@admin_required
def admin_gallery(request):
    gallery_items = GalleryItem.objects.order_by('-created_at')
    return render(request, 'core/admin_gallery.html', {'gallery_items': gallery_items})


@admin_required
def admin_gallery_create(request):
    if request.method == 'POST':
        form = GalleryItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Gallery image added successfully.')
            return redirect('core:admin_gallery')
    else:
        form = GalleryItemForm()
    return render(request, 'core/admin_gallery_form.html', {'form': form})


@admin_required
def admin_gallery_edit(request, gallery_id):
    gallery_item = get_object_or_404(GalleryItem, id=gallery_id)
    if request.method == 'POST':
        form = GalleryItemForm(request.POST, request.FILES, instance=gallery_item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Gallery image updated successfully.')
            return redirect('core:admin_gallery')
    else:
        form = GalleryItemForm(instance=gallery_item)
    return render(request, 'core/admin_gallery_form.html', {'form': form, 'gallery_item': gallery_item})


@admin_required
def admin_gallery_delete(request, gallery_id):
    gallery_item = get_object_or_404(GalleryItem, id=gallery_id)
    gallery_item.delete()
    messages.success(request, 'Gallery image removed successfully.')
    return redirect('core:admin_gallery')


@admin_required
def admin_banners(request):
    banners = Banner.objects.order_by('order', '-created_at')
    return render(request, 'core/admin_banners.html', {'banners': banners})


@admin_required
def admin_banner_create(request):
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Banner added successfully.')
            return redirect('core:admin_banners')
    else:
        form = BannerForm()
    return render(request, 'core/admin_banner_form.html', {'form': form})


@admin_required
def admin_banner_edit(request, banner_id):
    banner = get_object_or_404(Banner, id=banner_id)
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            messages.success(request, 'Banner updated successfully.')
            return redirect('core:admin_banners')
    else:
        form = BannerForm(instance=banner)
    return render(request, 'core/admin_banner_form.html', {'form': form, 'banner': banner})


@admin_required
def admin_banner_delete(request, banner_id):
    banner = get_object_or_404(Banner, id=banner_id)
    banner.delete()
    messages.success(request, 'Banner removed successfully.')
    return redirect('core:admin_banners')


@admin_required
def admin_announcement_create(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Announcement created successfully.')
            return redirect('core:admin_announcements')
    else:
        form = AnnouncementForm()
    return render(request, 'core/admin_announcement_form.html', {'form': form})


@admin_required
def admin_announcement_edit(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Announcement updated successfully.')
            return redirect('core:admin_announcements')
    else:
        form = AnnouncementForm(instance=announcement)
    return render(request, 'core/admin_announcement_form.html', {'form': form, 'announcement': announcement})


def register(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    login_form = UserLoginForm(request)
    next_url = request.GET.get('next', '')
    if request.method == 'POST':
        register_form = UserRegisterForm(request.POST)
        if register_form.is_valid():
            user = register_form.save(commit=False)
            if user.is_admin:
                user.role = 'student'
            user.is_active = True
            user.email_verified = False
            user.admin_approved = True
            user.approval_status = 'approved'
            user.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            messages.success(request, 'Registration successful. You are now logged in.')
            return redirect(next_url or 'core:home')
    else:
        register_form = UserRegisterForm()
    return render(request, 'core/auth.html', {
        'login_form': login_form,
        'register_form': register_form,
        'active_tab': 'register',
        'next': next_url,
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    register_form = UserRegisterForm()
    next_url = request.GET.get('next', '')
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user is not None:
                if not user.is_active:
                    messages.error(request, 'Your account is not active yet.')
                else:
                    login(request, user)
                    if not form.cleaned_data.get('remember_me'):
                        request.session.set_expiry(0)
                    redirect_url = request.POST.get('next') or request.GET.get('next')
                    return redirect(redirect_url or 'core:home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserLoginForm(request)
    return render(request, 'core/auth.html', {
        'login_form': form,
        'register_form': register_form,
        'active_tab': 'login',
        'next': next_url,
    })


def logout_view(request):
    logout(request)
    return redirect('core:login')


@login_required
def dashboard(request):
    user = request.user
    notifications = Notification.objects.filter(user=user, is_read=False)[:5]
    if user.is_admin:
        total_students = User.objects.filter(role__iexact='student').count()
        total_coordinators = User.objects.filter(role__iexact='coordinator').count()
        total_organizers = User.objects.filter(role__iexact='organizer').count()
        total_users = User.objects.exclude(role__iexact='admin').count()
        pending_events = Event.objects.filter(status='pending').count()
        total_registrations = Registration.objects.count()
        pending_registrations = Registration.objects.filter(approval_status='pending').count()
        total_paid_registrations = Registration.objects.filter(payment_status='paid').count()
        context = {
            'notifications': notifications,
            'total_students': total_students,
            'total_coordinators': total_coordinators,
            'total_organizers': total_organizers,
            'total_users': total_users,
            'pending_events': pending_events,
            'total_registrations': total_registrations,
            'pending_registrations': pending_registrations,
            'total_paid_registrations': total_paid_registrations,
        }
    else:
        registered_events = Registration.objects.filter(student=user).count()
        upcoming_events = Event.objects.filter(status='approved', date__gte=timezone.now().date()).count()
        context = {
            'notifications': notifications,
            'registered_events': registered_events,
            'upcoming_events': upcoming_events,
            'recent_events': Event.objects.filter(status='approved').order_by('date')[:5],
        }
    return render(request, 'core/dashboard.html', context)


@admin_required
def pending_users(request):
    managed_accounts = User.objects.exclude(role__iexact='admin').order_by('-date_joined')
    return render(request, 'core/pending_users.html', {'managed_accounts': managed_accounts})


@admin_required
def remove_user(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        messages.error(request, 'You cannot remove your own account from here.')
    elif target_user.is_admin:
        messages.error(request, 'Administrators cannot be removed from this page.')
    else:
        target_user.delete()
        messages.success(request, f'{target_user.username} has been removed.')
    return redirect('core:pending_users')


@admin_required
def admin_events(request):
    status = request.GET.get('status', '')
    events = Event.objects.all().order_by('-date')
    if status:
        events = events.filter(status=status)
    return render(request, 'core/admin_events.html', {
        'events': events,
        'status': status,
    })


@admin_required
def admin_event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    approval_form = EventApprovalForm(instance=event)
    participants = Registration.objects.filter(event=event).select_related('student').order_by('-registered_at')
    scan_feedback = None
    if request.method == 'POST' and request.POST.get('scan_qr'):
        token = request.POST.get('scan_token', '').strip()
        if token:
            try:
                payload = signing.loads(token)
                registration = Registration.objects.filter(
                    id=payload.get('registration_id'),
                    event=event,
                    qr_token=token,
                    approval_status='approved'
                ).select_related('student').first()
                if registration:
                    registration.attended = True
                    registration.attendance_time = timezone.now()
                    registration.save()
                    Attendance.objects.get_or_create(registration=registration, defaults={'scanned_by': request.user})
                    scan_feedback = ('success', f'Attendance marked for {registration.student.username}.')
                else:
                    scan_feedback = ('danger', 'No matching approved registration found for this QR code.')
            except signing.BadSignature:
                scan_feedback = ('danger', 'Invalid QR token. Please scan a valid registration QR code.')
        else:
            scan_feedback = ('warning', 'Please provide a QR token to scan.')
    return render(request, 'core/admin_event_detail.html', {
        'event': event,
        'approval_form': approval_form,
        'participants': participants,
        'scan_feedback': scan_feedback,
    })


@admin_required
def admin_participants(request):
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')
    events = Event.objects.prefetch_related('registrations__student').order_by('-date')
    if query:
        events = events.filter(title__icontains=query)
    if status:
        events = events.filter(status=status)
    return render(request, 'core/admin_participants.html', {
        'events': events,
        'query': query,
        'status': status,
    })


@admin_required
def admin_event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.status = 'approved'
            event.save()
            messages.success(request, 'New event added successfully.')
            return redirect('core:admin_events')
    else:
        form = EventForm()
    return render(request, 'core/admin_event_form.html', {'form': form})


@admin_required
def approve_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        form = EventApprovalForm(request.POST, instance=event)
        if form.is_valid():
            approved_event = form.save(commit=False)
            approved_event.approved_by = request.user
            approved_event.save()
            Notification.objects.create(
                user=event.coordinator or request.user,
                title='Event approved',
                message=f'Your event "{event.title}" has been approved by admin.',
            )
            if event.coordinator and event.coordinator.email:
                subject = 'Your CampusConnect event has been approved'
                message = render_to_string('emails/event_approved.txt', {
                    'event': event,
                    'admin': request.user,
                })
                html_message = render_to_string('emails/event_approved.html', {
                    'event': event,
                    'admin': request.user,
                })
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [event.coordinator.email],
                    html_message=html_message,
                    fail_silently=True,
                )
            messages.success(request, f'Event "{event.title}" approved.')
            return redirect('core:admin_event_detail', event_id=event.id)
    return redirect('core:admin_event_detail', event_id=event.id)


@admin_required
def reject_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        form = EventApprovalForm(request.POST, instance=event)
        if form.is_valid():
            rejected_event = form.save(commit=False)
            rejected_event.approved_by = request.user
            rejected_event.save()
            Notification.objects.create(
                user=event.coordinator or request.user,
                title='Event rejected',
                message=f'Your event "{event.title}" has been rejected by admin.',
            )
            if event.coordinator and event.coordinator.email:
                subject = 'Your CampusConnect event has been rejected'
                message = render_to_string('emails/event_rejected.txt', {
                    'event': event,
                    'admin': request.user,
                })
                html_message = render_to_string('emails/event_rejected.html', {
                    'event': event,
                    'admin': request.user,
                })
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [event.coordinator.email],
                    html_message=html_message,
                    fail_silently=True,
                )
            messages.success(request, f'Event "{event.title}" rejected.')
            return redirect('core:admin_event_detail', event_id=event.id)
    return redirect('core:admin_event_detail', event_id=event.id)


@admin_required
def mark_event_ongoing(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.status = 'ongoing'
    event.save()
    messages.success(request, f'Event "{event.title}" marked as ongoing.')
    return redirect('core:admin_event_detail', event_id=event.id)


@admin_required
def mark_event_completed(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.status = 'completed'
    event.save()
    messages.success(request, f'Event "{event.title}" marked as completed.')
    return redirect('core:admin_event_detail', event_id=event.id)


@login_required
def coordinator_dashboard(request):
    events = Event.objects.filter(coordinator=request.user).order_by('-date')
    return render(request, 'core/coordinator_dashboard.html', {'events': events})


@login_required
def coordinator_event_create(request):
    if not request.user.is_coordinator:
        messages.error(request, 'Only coordinators may create events.')
        return redirect('core:dashboard')
    if request.method == 'POST':
        form = CoordinatorEventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.coordinator = request.user
            event.status = 'pending'
            event.save()
            admin_user = User.objects.filter(role='admin', is_active=True).first()
            if admin_user:
                Notification.objects.create(
                    user=admin_user,
                    title='New event pending approval',
                    message=f'Event "{event.title}" is waiting for admin approval.',
                )
                subject = 'New CampusConnect event pending approval'
                message = render_to_string('emails/event_pending_admin.txt', {
                    'event': event,
                    'coordinator': request.user,
                })
                html_message = render_to_string('emails/event_pending_admin.html', {
                    'event': event,
                    'coordinator': request.user,
                })
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [admin_user.email],
                    html_message=html_message,
                    fail_silently=True,
                )
            messages.success(request, 'Event created successfully and sent for approval.')
            return redirect('core:coordinator_dashboard')
    else:
        form = CoordinatorEventForm()
    return render(request, 'core/coordinator_event_form.html', {'form': form})


@login_required
def coordinator_event_edit(request, event_id):
    if not request.user.is_coordinator:
        messages.error(request, 'Only coordinators may edit events.')
        return redirect('core:dashboard')
    event = get_object_or_404(Event, id=event_id, coordinator=request.user)
    if request.method == 'POST':
        form = CoordinatorEventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            event = form.save(commit=False)
            event.status = 'pending'
            event.approved_by = None
            event.save()
            messages.success(request, 'Event updated successfully and resent for approval.')
            return redirect('core:coordinator_dashboard')
    else:
        form = CoordinatorEventForm(instance=event)
    return render(request, 'core/coordinator_event_form.html', {'form': form, 'event': event})


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('core:profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'core/profile.html', {'form': form})


def event_list(request):
    category = request.GET.get('category')
    query = request.GET.get('q')
    events = Event.objects.filter(status='approved').order_by('date')
    if category:
        events = events.filter(category=category)
    if query:
        events = events.filter(title__icontains=query)
    categories = Event._meta.get_field('category').choices
    registered_event_ids = set()
    if request.user.is_authenticated and request.user.is_student:
        registered_event_ids = set(Registration.objects.filter(student=request.user).values_list('event_id', flat=True))
    return render(request, 'core/event_list.html', {
        'events': events,
        'categories': categories,
        'registered_event_ids': registered_event_ids,
    })


def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    registration = None
    register_form = None
    if request.user.is_authenticated and request.user.is_student:
        registration = Registration.objects.filter(event=event, student=request.user).first()
        if request.method == 'POST':
            form = EventRegistrationForm(request.POST)
            if form.is_valid():
                if not event.is_registration_open:
                    messages.error(request, 'Registration for this event is closed.')
                    return redirect('core:event_detail', event_id=event.id)
                registration, created = Registration.objects.get_or_create(event=event, student=request.user)
                if not created:
                    messages.info(request, 'You already submitted registration for this event. It is awaiting approval.')
                else:
                    registration.note = form.cleaned_data.get('note', '')
                    registration.approval_status = 'pending'
                    registration.payment_status = 'pending'
                    registration.save()
                    admin_user = User.objects.filter(role='admin', is_active=True).first()
                    if admin_user:
                        Notification.objects.create(
                            user=admin_user,
                            title='New event registration pending approval',
                            message=f'{request.user.username} has requested participation in {event.title}.',
                        )
                    messages.success(request, 'Your event registration has been submitted and is awaiting administrator approval.')
                return redirect('core:event_detail', event_id=event.id)
            register_form = form
        else:
            register_form = EventRegistrationForm()
    return render(request, 'core/event_detail.html', {
        'event': event,
        'registration': registration,
        'register_form': register_form,
    })


@login_required
def event_register(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if not request.user.is_student:
        messages.error(request, 'Only students may register for events.')
        return redirect('core:event_detail', event_id=event.id)
    if not event.is_registration_open:
        messages.error(request, 'Registration for this event is not currently open.')
        return redirect('core:event_detail', event_id=event.id)

    registration, created = Registration.objects.get_or_create(event=event, student=request.user)
    if not created:
        messages.info(request, 'You already submitted registration for this event. It is awaiting approval.')
        return redirect('core:my_events')

    registration.approval_status = 'pending'
    registration.payment_status = 'pending'
    registration.save()
    admin_user = User.objects.filter(role='admin', is_active=True).first()
    if admin_user:
        Notification.objects.create(
            user=admin_user,
            title='New event registration pending approval',
            message=f'{request.user.username} has requested participation in {event.title}.',
        )
    messages.success(request, 'Event registration submitted and pending approval.')
    return redirect('core:my_events')


@login_required
def event_pay(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    registration = Registration.objects.filter(event=event, student=request.user, approval_status='approved').first()
    if not registration:
        messages.error(request, 'You must have an approved registration before payment.')
        return redirect('core:event_detail', event_id=event.id)

    if not event.is_paid_event:
        messages.error(request, 'This event does not require payment.')
        return redirect('core:event_detail', event_id=event.id)

    if registration.payment_status == 'paid':
        messages.info(request, 'Your payment is already completed.')
        return redirect('core:event_detail', event_id=event.id)

    if request.method == 'POST':
        registration.payment_status = 'paid'
        registration.save()
        messages.success(request, 'Payment received. Your QR pass can now be downloaded once verified.')
        return redirect('core:my_events')

    return render(request, 'core/event_payment.html', {
        'event': event,
        'registration': registration,
    })


@login_required
def my_events(request):
    registrations = Registration.objects.filter(student=request.user).select_related('event')
    return render(request, 'core/my_events.html', {'registrations': registrations})


@login_required
def notifications(request):
    notes = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/notifications.html', {'notifications': notes})


def announcements(request):
    announcements = Announcement.objects.order_by('-publish_date')
    return render(request, 'core/announcements.html', {'announcements': announcements})

@admin_required
def pending_registrations(request):
    query = request.GET.get('q', '')
    registrations = Registration.objects.filter(approval_status='pending').select_related('student', 'event').order_by('-registered_at')
    if query:
        registrations = registrations.filter(
            event__title__icontains=query
        )
    return render(request, 'core/pending_registrations.html', {'registrations': registrations, 'query': query})

@admin_required
def approve_registration(request, registration_id):
    registration = get_object_or_404(Registration, id=registration_id, approval_status='pending')
    registration.approval_status = 'approved'
    registration.save()
    payload = {
        'student_id': registration.student.id,
        'student_name': registration.student.username,
        'registration_id': registration.id,
        'event_id': registration.event.id,
        'event_name': registration.event.title,
        'timestamp': timezone.now().isoformat(),
    }
    registration.qr_token = signing.dumps(payload)
    qr = qrcode.make(registration.qr_token)
    buffer = io.BytesIO()
    qr.save(buffer, format='PNG')
    registration.qr_code.save(f'registration_{registration.id}.png', buffer, save=True)
    registration.save()
    Notification.objects.create(
        user=registration.student,
        title='Event registration approved',
        message=f'Your registration for {registration.event.title} has been approved. Your QR code is ready.',
    )
    messages.success(request, f'Registration for {registration.student.username} approved.')
    return redirect('core:pending_registrations')

@admin_required
def reject_registration(request, registration_id):
    registration = get_object_or_404(Registration, id=registration_id, approval_status='pending')
    registration.approval_status = 'rejected'
    registration.save()
    Notification.objects.create(
        user=registration.student,
        title='Event registration rejected',
        message=f'Your registration for {registration.event.title} has been rejected by admin.',
    )
    messages.success(request, f'Registration for {registration.student.username} rejected.')
    return redirect('core:pending_registrations')
