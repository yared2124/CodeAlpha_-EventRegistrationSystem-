from rest_framework import permissions

class CanCancelRegistration(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.user == request.user:
            return True
        if obj.event.organizer == request.user:
            return True
        return False