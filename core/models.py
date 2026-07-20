from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('student', 'Student'),
    ('coordinator', 'Faculty/Event Coordinator'),
    ('organizer', 'Club Organizer'),
]

CATEGORY_CHOICES = [
    ('technical', 'Technical'),
    ('cultural', 'Cultural'),
    ('sports', 'Sports'),
    ('workshop', 'Workshop'),
    ('seminar', 'Seminar'),
    ('hackathon', 'Hackathon'),
    ('competition', 'Competition'),
    ('webinar', 'Webinar'),
    ('festival', 'Festival'),
]

STATUS_CHOICES = [
    ('pending', 'Pending Approval'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('ongoing', 'Ongoing'),
    ('completed', 'Completed'),
]

class User(AbstractUser):
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    email_verified = models.BooleanField(default=False)
    admin_approved = models.BooleanField(default=False)
    approval_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending Approval'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='pending',
    )
    phone = models.CharField(max_length=20, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    @property
    def is_admin(self):
        return str(self.role).strip().lower() == 'admin'

    def is_approved(self):
        return self.email_verified and self.admin_approved and self.is_active

    def can_login(self):
        return self.is_approved() or self.is_superuser

    def save(self, *args, **kwargs):
        if isinstance(self.role, str):
            self.role = self.role.strip().lower()
        if self.role not in dict(ROLE_CHOICES):
            self.role = 'student'
        super().save(*args, **kwargs)

    @property
    def is_student(self):
        return str(self.role).strip().lower() == 'student'

    @property
    def is_coordinator(self):
        return str(self.role).strip().lower() == 'coordinator'

    @property
    def is_organizer(self):
        return str(self.role).strip().lower() == 'organizer'

class Club(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    organizer = models.ForeignKey(User, limit_choices_to={'role': 'organizer'}, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ClubMember(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='members')
    student = models.ForeignKey(User, limit_choices_to={'role': 'student'}, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('club', 'student')

    def __str__(self):
        return f"{self.student.username} in {self.club.name}"

class Event(models.Model):
    title = models.CharField(max_length=220)
    description = models.TextField()
    banner = models.ImageField(upload_to='events/banners/', blank=True, null=True)
    venue = models.CharField(max_length=220)
    date = models.DateField()
    time = models.TimeField()
    registration_deadline = models.DateTimeField()
    max_participants = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    coordinator = models.ForeignKey(User, limit_choices_to={'role': 'coordinator'}, on_delete=models.SET_NULL, null=True)
    approved_by = models.ForeignKey(User, limit_choices_to={'role': 'admin'}, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_events')
    approval_notes = models.TextField(blank=True)
    is_paid_event = models.BooleanField(default=False)
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, default='USD', blank=True)
    payment_deadline = models.DateTimeField(null=True, blank=True)
    club = models.ForeignKey(Club, on_delete=models.SET_NULL, null=True, blank=True)
    rules = models.TextField(blank=True)
    contact_info = models.CharField(max_length=220, blank=True)
    prize_details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_registration_open(self):
        return timezone.now() < self.registration_deadline and self.status == 'approved' and self.participant_count < self.max_participants

    @property
    def participant_count(self):
        return self.registrations.count()

    @property
    def paid_registration_count(self):
        return self.registrations.filter(payment_status='paid').count()

    @property
    def total_revenue(self):
        if not self.is_paid_event or not self.entry_fee:
            return 0
        return self.entry_fee * self.paid_registration_count

    @property
    def is_full(self):
        return self.participant_count >= self.max_participants

    def __str__(self):
        return self.title

class Registration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    student = models.ForeignKey(User, limit_choices_to={'role': 'student'}, on_delete=models.CASCADE)
    note = models.TextField(blank=True)
    payment_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed'), ('refunded', 'Refunded')], default='pending')
    approval_status = models.CharField(max_length=20, choices=[('pending', 'Pending Approval'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    registered_at = models.DateTimeField(auto_now_add=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    qr_token = models.CharField(max_length=512, blank=True)
    attended = models.BooleanField(default=False)
    attendance_time = models.DateTimeField(null=True, blank=True)
    certificate_generated = models.BooleanField(default=False)

    class Meta:
        unique_together = ('event', 'student')

    def __str__(self):
        return f"{self.student.username} -> {self.event.title}"

class Attendance(models.Model):
    registration = models.OneToOneField(Registration, on_delete=models.CASCADE, related_name='attendance')
    scanned_at = models.DateTimeField(auto_now_add=True)
    scanned_by = models.ForeignKey(User, limit_choices_to={'role__in': ['admin', 'coordinator']}, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Attendance {self.registration.student.username} for {self.registration.event.title}"

class Certificate(models.Model):
    registration = models.OneToOneField(Registration, on_delete=models.CASCADE, related_name='certificate')
    generated_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='certificates/')

    def __str__(self):
        return f"Certificate {self.registration.student.username} - {self.registration.event.title}"

class Winner(models.Model):
    event = models.ForeignKey(Event, related_name='winners', on_delete=models.CASCADE)
    student = models.ForeignKey(User, limit_choices_to={'role': 'student'}, on_delete=models.CASCADE)
    position = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.position}: {self.student.username}"

class GalleryItem(models.Model):
    title = models.CharField(max_length=120)
    image = models.ImageField(upload_to='gallery/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Banner(models.Model):
    title = models.CharField(max_length=120, blank=True)
    subtitle = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='banners/')
    button_text = models.CharField(max_length=80, blank=True)
    button_url = models.CharField(max_length=220, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title or f'Banner {self.id}'

class Feedback(models.Model):
    student = models.ForeignKey(User, limit_choices_to={'role': 'student'}, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    comments = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.student.username}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=160)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification to {self.user.username}: {self.title}"

class Announcement(models.Model):
    title = models.CharField(max_length=220)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    publish_date = models.DateField(default=timezone.now)

    def __str__(self):
        return self.title
