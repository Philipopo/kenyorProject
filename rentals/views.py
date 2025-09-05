# rentals/views.py
from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Equipment, Rental, RentalPayment
from .serializers import EquipmentSerializer, RentalSerializer, RentalPaymentSerializer
from accounts.permissions import DynamicPermission

class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [permissions.IsAuthenticated, DynamicPermission]
    page_permission_name = 'rentals_equipment'
    # POST checks 'create_equipment' via DynamicPermission.CREATE_ACTIONS

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

class RentalViewSet(viewsets.ModelViewSet):
    queryset = Rental.objects.select_related('renter', 'equipment').all()
    serializer_class = RentalSerializer
    permission_classes = [permissions.IsAuthenticated, DynamicPermission]
    page_permission_name = 'rentals_active'
    # POST checks 'create_rental' via DynamicPermission.CREATE_ACTIONS

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})  # Ensure serializer sees request.user
        return context

    def perform_create(self, serializer):
        serializer.save(renter=self.request.user)  # Set renter to current user

class RentalPaymentViewSet(viewsets.ModelViewSet):
    queryset = RentalPayment.objects.select_related('rental__renter', 'rental__equipment').all()
    serializer_class = RentalPaymentSerializer
    permission_classes = [permissions.IsAuthenticated, DynamicPermission]
    page_permission_name = 'rentals_payments'
    # POST checks 'create_payment' via DynamicPermission.CREATE_ACTIONS

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context