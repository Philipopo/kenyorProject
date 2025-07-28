
from rest_framework.permissions import BasePermission

ROLE_LEVELS = {
    'staff': 1,
    'finance_manager': 2,
    'operations_manager': 3,
    'md': 4,
    'admin': 5,
}

class HasMinimumRole(BasePermission):
    """
    Grant access only if user has the required role level or higher.
    """

    def has_permission(self, request, view):
        required_level = getattr(view, 'required_role_level', 1)
        user_role = getattr(request.user, 'role', 'staff')
        user_level = ROLE_LEVELS.get(user_role.lower(), 0)  # fix: ensure lowercase
        return user_level >= required_level
        


