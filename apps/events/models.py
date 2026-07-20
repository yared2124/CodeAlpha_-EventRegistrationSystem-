from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


class Event(models.Model):
    # Choices for event status
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled'),
    )

    # ---- Core fields ----
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organized_events'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=255)

    # ---- Capacity & Booking ----
    capacity = models.PositiveIntegerField(help_text="Maximum number of attendees")
    # Denormalized count – updated atomically to avoid race conditions
    filled_seats = models.PositiveIntegerField(default=0)

    # ---- Status & Timestamps ----
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'events'
        # Indexes for faster filtering & sorting
        indexes = [
            models.Index(fields=['status', 'start_date']),          # Homepage queries
            models.Index(fields=['organizer', 'status']),          # Organizer dashboards
            models.Index(fields=['start_date']),                   # Chronological listings
        ]
        ordering = ['-start_date']  # Default ordering

    def __str__(self):
        return f"{self.title} – {self.start_date.strftime('%Y-%m-%d')}"

    # ---- Business logic properties ----
    @property
    def available_seats(self):
        """Remaining capacity – calculated from the denormalized field."""
        return max(self.capacity - self.filled_seats, 0)

    @property
    def is_full(self):
        return self.filled_seats >= self.capacity

    @property
    def is_past(self):
        """True if the event has already ended."""
        return self.end_date < timezone.now()

    # ---- Validation ----
    def clean(self):
        # Ensure end_date is after start_date
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValidationError('End date must be after start date.')
        # Ensure capacity is at least 1
        if self.capacity < 1:
            raise ValidationError('Capacity must be at least 1.')

    def save(self, *args, **kwargs):
        self.full_clean()  # Calls clean() automatically
        super().save(*args, **kwargs)