from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


class Event(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled'),
    )

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
    capacity = models.PositiveIntegerField(help_text="Maximum number of attendees")
    filled_seats = models.PositiveIntegerField(default=0)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['status', 'start_date']),
            models.Index(fields=['organizer', 'status']),
            models.Index(fields=['start_date']),
        ]
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.title} – {self.start_date.strftime('%Y-%m-%d')}"

    @property
    def available_seats(self):
        return max(self.capacity - self.filled_seats, 0)

    @property
    def is_full(self):
        return self.filled_seats >= self.capacity

    @property
    def is_past(self):
        return self.end_date < timezone.now()

    def clean(self):
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValidationError('End date must be after start date.')
        if self.capacity < 1:
            raise ValidationError('Capacity must be at least 1.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)