from rest_framework import permissions


class IsCoreOrganizer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_core_organizer


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.speaker == request.user
