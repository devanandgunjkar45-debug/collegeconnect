from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import get_user_model
from .models import Banner, Event, Feedback, GalleryItem, Club, Announcement, ROLE_CHOICES

User = get_user_model()
REGISTER_ROLE_CHOICES = [choice for choice in ROLE_CHOICES if choice[0] != 'admin']

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=REGISTER_ROLE_CHOICES,
        initial='student',
        widget=forms.Select(attrs={'class': 'form-select form-select-lg'}),
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'role', 'password1', 'password2']

    def clean_role(self):
        role = self.cleaned_data.get('role')
        if isinstance(role, str):
            normalized_role = role.strip().lower()
            if normalized_role == 'admin':
                raise forms.ValidationError('Admin role cannot be selected during registration.')
            return normalized_role
        return role

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already registered.')
        return email

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Username or email',
        widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': 'Username or email'})
    )
    remember_me = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'profile_image']

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'banner', 'venue', 'date', 'time',
            'registration_deadline', 'max_participants', 'category',
            'coordinator', 'club', 'is_paid_event', 'entry_fee', 'currency', 'payment_deadline',
            'rules', 'contact_info', 'prize_details', 'status'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'registration_deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'payment_deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'entry_fee': forms.NumberInput(attrs={'type': 'number', 'step': '0.01'}),
            'is_paid_event': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        is_paid_event = cleaned_data.get('is_paid_event')
        entry_fee = cleaned_data.get('entry_fee')
        payment_deadline = cleaned_data.get('payment_deadline')
        if is_paid_event:
            if not entry_fee or entry_fee <= 0:
                self.add_error('entry_fee', 'Paid events require a positive entry fee.')
            if not payment_deadline:
                self.add_error('payment_deadline', 'Paid events require a payment deadline.')
        return cleaned_data

class CoordinatorEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'banner', 'venue', 'date', 'time',
            'registration_deadline', 'max_participants', 'category',
            'club', 'is_paid_event', 'entry_fee', 'currency', 'payment_deadline',
            'rules', 'contact_info', 'prize_details'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'registration_deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'payment_deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'entry_fee': forms.NumberInput(attrs={'type': 'number', 'step': '0.01'}),
            'is_paid_event': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        is_paid_event = cleaned_data.get('is_paid_event')
        entry_fee = cleaned_data.get('entry_fee')
        payment_deadline = cleaned_data.get('payment_deadline')
        if is_paid_event:
            if not entry_fee or entry_fee <= 0:
                self.add_error('entry_fee', 'Paid events require a positive entry fee.')
            if not payment_deadline:
                self.add_error('payment_deadline', 'Paid events require a payment deadline.')
        return cleaned_data

class EventApprovalForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['status', 'approval_notes']
        widgets = {
            'approval_notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['name', 'description', 'organizer']

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your email'}))
    subject = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'How can we help you?'}))

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'message', 'publish_date']
        widgets = {
            'publish_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class GalleryItemForm(forms.ModelForm):
    class Meta:
        model = GalleryItem
        fields = ['title', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['title', 'subtitle', 'image', 'button_text', 'button_url', 'order', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'subtitle': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'button_text': forms.TextInput(attrs={'class': 'form-control'}),
            'button_url': forms.URLInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class EventRegistrationForm(forms.Form):
    note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Add a short note for the event organizer (optional)',
        }),
        label='Participation Note',
    )

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['event', 'rating', 'comments']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }
