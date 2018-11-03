# -*- coding: utf-8 -*-

# nexus Stuff
# Jumpstart Stuff
from nexus.base.exceptions import PermissionDenied


def can_accept_proposal(user, obj):
    if user.is_core_organizer:
        return True
    return False


def can_retract_proposal(user, obj):
    if user.is_core_organizer or obj.speaker == user:
        return True
    return False


def can_modify_proposal(user, obj):
    if user.is_core_organizer or obj.speaker == user:
        return True
    return False


PERMISSIONS = {
    'can_accept_proposal': can_accept_proposal,
    'can_retract_proposal': can_retract_proposal,
    'can_modify_proposal': can_modify_proposal,
}


def has_perm(permission_name, user, obj=None, raise_exception=False):
    func = PERMISSIONS[permission_name]

    if func(user, obj):
        return True

    # In case the 403 handler should be called raise the exception
    if raise_exception:
        raise PermissionDenied

    return False
