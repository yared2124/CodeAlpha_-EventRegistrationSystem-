from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid


class Registration(models.Model):
    STATUS_CHOICES = (
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('waitlisted', 'Waitlisted'),
    )

    # ---- Relationships ----
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='registrations'
    )
    event = models.ForeignKey(
        'events.Event',
        on_delete=models.CASCADE,
        related_name='registrations'
    )

    # ---- Status & Ticket ----
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='confirmed'
    )
    ticket_number = models.CharField(max_length=20, unique=True, blank=True)

    # ---- Timestamps ----
    registered_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'registrations'
        unique_together = [['user', 'event']]
        indexes = [
            models.Index(fields=['event', 'status']),
            models.Index(fields=['user', 'event']),
        ]
        ordering = ['-registered_at']

    def __str__(self):
        return f"{self.user.email} – {self.event.title} ({self.status})"

    def cancel(self):
        """Cancel a confirmed registration and free up the seat."""
        if self.status == 'cancelled':
            raise ValueError("Registration is already cancelled.")
        if self.event.is_past:
            raise ValueError("Cannot cancel a past event registration.")
        self.status = 'cancelled'
        self.cancelled_at = timezone.now()
        from django.db.models import F
        self.event.filled_seats = F('filled_seats') - 1
        self.event.save(update_fields=['filled_seats'])
        self.save()

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = self._generate_ticket_number()
        super().save(*args, **kwargs)

    def _generate_ticket_number(self):
        return f"TIX-{uuid.uuid4().hex[:8].upper()}"

    def clean(self):
        if self.user == self.event.organizer:
            raise ValidationError("Organizers cannot register for their own events.")
        if self.event.status != 'published':
            raise ValidationError("This event is not open for registration.")
        if self.event.is_past:
            raise ValidationError("This event has already passed.")