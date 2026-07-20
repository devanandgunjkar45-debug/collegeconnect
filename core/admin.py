from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import (
    User, Club, ClubMember, Event, Registration, Attendance, Certificate,
    Winner, GalleryItem, Banner, Feedback, Notification, Announcement
)

@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    fieldsets = DefaultUserAdmin.fieldsets + (
        ('Role & Profile', {'fields': ('role', 'email_verified', 'admin_approved', 'approval_status', 'phone', 'profile_image')}),
    )
    list_display = ('username', 'email', 'role', 'approval_status', 'admin_approved', 'is_active', 'is_staff')
    list_filter = ('role', 'approval_status', 'admin_approved', 'is_staff', 'is_active')
    actions = ['approve_users', 'reject_users']

    def approve_users(self, request, queryset):
        updated = queryset.update(admin_approved=True, approval_status='approved', is_active=True)
        self.message_user(request, f'{updated} user(s) approved.')
    approve_users.short_description = 'Approve selected users'

    def reject_users(self, request, queryset):
        updated = queryset.update(admin_approved=False, approval_status='rejected', is_active=False)
        self.message_user(request, f'{updated} user(s) rejected.')
    reject_users.short_description = 'Reject selected users'

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'date', 'venue', 'coordinator', 'approved_by', 'participant_count')
    list_filter = ('status', 'category', 'coordinator', 'date')
    search_fields = ('title', 'description', 'venue', 'contact_info')
    actions = ['approve_events', 'reject_events', 'mark_ongoing', 'mark_completed']

    def participant_count(self, obj):
        return obj.participant_count
    participant_count.short_description = 'Participants'

    def approve_events(self, request, queryset):
        updated = queryset.update(status='approved', approved_by=request.user)
        self.message_user(request, f'{updated} event(s) approved.')
    approve_events.short_description = 'Approve selected events'

    def reject_events(self, request, queryset):
        updated = queryset.update(status='rejected', approved_by=request.user)
        self.message_user(request, f'{updated} event(s) rejected.')
    reject_events.short_description = 'Reject selected events'

    def mark_ongoing(self, request, queryset):
        updated = queryset.update(status='ongoing')
        self.message_user(request, f'{updated} event(s) marked ongoing.')
    mark_ongoing.short_description = 'Mark selected events as ongoing'

    def mark_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} event(s) marked completed.')
    mark_completed.short_description = 'Mark selected events as completed'

admin.site.register(Club)
admin.site.register(ClubMember)
# admin.site.register(Event) removed because EventAdmin manages it
admin.site.register(Registration)
admin.site.register(Attendance)
admin.site.register(Certificate)
admin.site.register(Winner)
admin.site.register(GalleryItem)
admin.site.register(Banner)
admin.site.register(Feedback)
admin.site.register(Notification)
admin.site.register(Announcement)
