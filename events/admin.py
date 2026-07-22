from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'start_date', 'status', 'capacity', 'filled_seats', 'available_seats')
    list_filter = ('status', 'start_date', 'organizer')
    search_fields = ('title', 'location', 'organizer__email')
    readonly_fields = ('created_at', 'updated_at', 'filled_seats')
    fieldsets = (
        ('Basic Info', {'fields': ('title', 'description', 'location')}),
        ('Date & Time', {'fields': ('start_date', 'end_date')}),
        ('Capacity', {'fields': ('capacity', 'filled_seats')}),
        ('Status', {'fields': ('status',)}),
        ('Metadata', {'fields': ('created_at', 'updated_at')}),
    )

    def get_readonly_fields(self, request, obj=None):
        # 'available_seats' is a property, not a DB field – make it read-only
        return self.readonly_fields + ('available_seats',)

    def available_seats(self, obj):
        return obj.available_seats
    available_seats.short_description = 'Available Seats'

    def save_model(self, request, obj, form, change):
        # If creating a new event, set the organizer to the logged‑in user
        if not change:
            obj.organizer = request.user
        super().save_model(request, obj, form, change)