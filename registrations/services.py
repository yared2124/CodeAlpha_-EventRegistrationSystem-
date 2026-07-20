from django.db import transaction, IntegrityError
from django.db.models import F
from django.utils import timezone
from events.models import Event
from registrations.models import Registration
import uuid
import logging

logger = logging.getLogger(__name__)

class RegistrationService:
    @staticmethod
    @transaction.atomic
    def register_user(user, event_id):
        event = Event.objects.select_for_update().get(id=event_id)

        if event.status != 'published':
            raise ValueError("Event is not open for registration.")
        if event.start_date < timezone.now():
            raise ValueError("Event has already started.")

        updated = Event.objects.filter(
            id=event_id,
            filled_seats__lt=F('capacity')
        ).update(filled_seats=F('filled_seats') + 1)

        if updated == 0:
            raise RuntimeError("Event capacity has been reached.")

        try:
            registration = Registration.objects.create(
                user=user,
                event=event,
                ticket_number=RegistrationService._generate_ticket_number()
            )
            logger.info(f"User {user.id} registered for event {event_id}")
            return registration
        except IntegrityError:
            raise ValueError("User is already registered for this event.")

    @staticmethod
    def _generate_ticket_number():
        return f"TIX-{uuid.uuid4().hex[:8].upper()}"

    @staticmethod
    @transaction.atomic
    def cancel_registration(registration, user):
        if registration.user != user and not user.is_staff:
            raise PermissionError("You cannot cancel this registration.")

        if registration.status == 'cancelled':
            raise ValueError("Registration already cancelled.")

        if registration.event.is_past:
            raise ValueError("Cannot cancel a past event registration.")

        Event.objects.filter(id=registration.event.id).update(
            filled_seats=F('filled_seats') - 1
        )

        registration.status = 'cancelled'
        registration.cancelled_at = timezone.now()
        registration.save(update_fields=['status', 'cancelled_at'])
        logger.info(f"Registration {registration.id} cancelled by user {user.id}")
        return registration