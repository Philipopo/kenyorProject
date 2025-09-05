# warehouse/views.py
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import WarehouseItem
from .serializers import WarehouseItemSerializer, ProductSerialNumberSerializer
from product_documentation.models import ProductSerialNumber
from accounts.models import PagePermission, ActionPermission, ROLE_LEVELS

def get_user_role_level(user):
    return ROLE_LEVELS.get(user.role, 0)

def get_page_required_level(page):
    perm = PagePermission.objects.filter(page_name=page).first()
    if not perm:
        return 1
    return ROLE_LEVELS.get(perm.min_role, 1)

def get_action_required_level(action_name: str) -> int:
    try:
        perm = ActionPermission.objects.get(action_name=action_name)
        return ROLE_LEVELS.get(perm.min_role, 1)
    except ActionPermission.DoesNotExist:
        return 1

def check_permission(user, page=None, action=None):
    user_level = get_user_role_level(user)
    if page:
        required = get_page_required_level(page)
        if user_level < required:
            raise PermissionDenied(f"Access denied: {page} requires role level {required}")
    if action:
        required = get_action_required_level(action)
        if user_level < required:
            raise PermissionDenied(f"Access denied: {action} requires role level {required}")

class WarehouseItemViewSet(viewsets.ModelViewSet):
    serializer_class = WarehouseItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        check_permission(self.request.user, page="warehouse")
        return WarehouseItem.objects.all()

    def perform_create(self, serializer):
        check_permission(self.request.user, action="create_warehouse_item")
        serializer.save(updated_by=self.request.user)

    def perform_update(self, serializer):
        check_permission(self.request.user, action="update_warehouse_item")
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        check_permission(self.request.user, action="delete_warehouse_item")
        instance.delete()

    @action(detail=False, methods=['get'], url_path='available_serials')
    def available_serials(self, request):
        check_permission(self.request.user, page="warehouse")
        serials = ProductSerialNumber.objects.filter(
            status='in_stock',
            warehouse_items__isnull=True
        )
        serializer = ProductSerialNumberSerializer(serials, many=True)
        return Response(serializer.data)