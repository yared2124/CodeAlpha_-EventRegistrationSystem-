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
    # Show available_seats as a computed property in the detail view
    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + ('available_seats',)

    # Display available seats in the list
    def available_seats(self, obj):
        return obj.available_seats
    available_seats.short_description = 'Available Seats'