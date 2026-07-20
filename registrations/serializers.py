from rest_framework import serializers
from registrations.models import Registration
from events.serializers import EventListSerializer

class RegistrationSerializer(serializers.ModelSerializer):
    event = EventListSerializer(read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Registration
        fields = ['id', 'event', 'status', 'ticket_number', 'registered_at', 'user_email']