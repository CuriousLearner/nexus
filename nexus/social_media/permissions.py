# Third Party Stuff
from rest_framework import permissions


class IsAdminOrAuthorOfPost(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.method in permissions.SAFE_METHODS:
            return True
        return request.user == obj.posted_by


class IsCoreOrganizer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_core_organizer:
            return True
