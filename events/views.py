from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.db.models import Count, Exists, OuterRef, Q, F
from django.db.models.functions import Coalesce
from django.db import models
from events.models import Event                       # <-- changed
from events.serializers import EventListSerializer, EventDetailSerializer
from registrations.models import Registration          # <-- changed
from registrations.services import RegistrationService
from registrations.serializers import RegistrationSerializer
from events.permissions import IsOrganizerOrReadOnly

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.filter(status='published')
    permission_classes = [IsAuthenticatedOrReadOnly, IsOrganizerOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            queryset = queryset.annotate(
                total_registrations=Count('registrations', filter=Q(registrations__status='confirmed')),
                available_seats=Coalesce(
                    F('capacity') - F('filled_seats'),
                    value=0,
                    output_field=models.IntegerField()
                )
            )
            if self.request.user.is_authenticated:
                queryset = queryset.annotate(
                    user_is_registered=Exists(
                        Registration.objects.filter(
                            event=OuterRef('pk'),
                            user=self.request.user,
                            status='confirmed'
                        )
                    )
                )
            return queryset
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return EventListSerializer
        return EventDetailSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def register(self, request, pk=None):
        try:
            registration = RegistrationService.register_user(request.user, pk)
            serializer = RegistrationSerializer(registration)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except RuntimeError as e:
            return Response({'detail': str(e)}, status=status.HTTP_409_CONFLICT)