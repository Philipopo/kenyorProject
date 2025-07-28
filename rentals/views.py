from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Equipment, Rental, RentalPayment
from .serializers import EquipmentSerializer, RentalSerializer, RentalPaymentSerializer

class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [permissions.IsAuthenticated]

# rentals/views.py
class RentalViewSet(viewsets.ModelViewSet):
    queryset = Rental.objects.select_related('renter', 'equipment').all()
    serializer_class = RentalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})  # ✅ ensure serializer sees request.user
        return context


class RentalPaymentViewSet(viewsets.ModelViewSet):
    queryset = RentalPayment.objects.select_related('rental__renter', 'rental__equipment').all()
    serializer_class = RentalPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
