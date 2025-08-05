
from rest_framework.permissions import BasePermission
from .models import PagePermission, ActionPermission

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
        

class DynamicPermission(BasePermission):
    def has_permission(self, request, view):
        # Check if the view requires a page permission
        page_name = getattr(view, 'page_permission_name', None)
        action_name = getattr(view, 'action_permission_name', None)

        user_role = request.user.role
        user_level = ROLE_HIERARCHY.get(user_role, 0)

        # Page check
        if page_name:
            try:
                page_perm = PagePermission.objects.get(page_name=page_name)
                required_level = ROLE_HIERARCHY[page_perm.min_role]
                if user_level < required_level:
                    return False
            except PagePermission.DoesNotExist:
                return False  # No config = deny

        # Action check
        if action_name:
            try:
                action_perm = ActionPermission.objects.get(action_name=action_name)
                required_level = ROLE_HIERARCHY[action_perm.min_role]
                if user_level < required_level:
                    return False
            except ActionPermission.DoesNotExist:
                return False  # No config = deny

        return True


