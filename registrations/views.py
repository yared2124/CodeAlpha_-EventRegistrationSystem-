from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.registrations.models import Registration
from apps.registrations.serializers import RegistrationSerializer
from apps.registrations.services import RegistrationService
from apps.registrations.permissions import CanCancelRegistration

class RegistrationViewSet(viewsets.ModelViewSet):
    serializer_class = RegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Registration.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def cancel(self, request, pk=None):
        registration = self.get_object()
        self.check_object_permissions(request, registration)
        try:
            updated = RegistrationService.cancel_registration(registration, request.user)
            serializer = self.get_serializer(updated)
            return Response(serializer.data)
        except (ValueError, PermissionError) as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)