from rest_framework import serializers
from events.models import Event

class EventListSerializer(serializers.ModelSerializer):
    available_seats = serializers.IntegerField(read_only=True)
    user_is_registered = serializers.BooleanField(read_only=True, default=False)
    organizer_email = serializers.EmailField(source='organizer.email', read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'start_date', 'location',
            'available_seats', 'user_is_registered', 'organizer_email'
        ]

class EventDetailSerializer(serializers.ModelSerializer):
    available_seats = serializers.IntegerField(read_only=True)
    organizer = serializers.StringRelatedField(read_only=True)
    total_registrations = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = '__all__'