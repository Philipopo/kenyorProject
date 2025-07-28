from rest_framework import serializers
from .models import Equipment, Rental, RentalPayment

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = '__all__'

# rentals/serializers.py
class RentalSerializer(serializers.ModelSerializer):
    renter_name = serializers.CharField(source='renter.full_name', read_only=True)
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)

    class Meta:
        model = Rental
        fields = '__all__'
        read_only_fields = ['renter']  # ✅ prevent manual setting from frontend

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['renter'] = request.user  # ✅ auto-assign logged-in user
        return super().create(validated_data)


class RentalPaymentSerializer(serializers.ModelSerializer):
    renter_name = serializers.CharField(source='rental.renter.full_name', read_only=True)
    equipment_name = serializers.CharField(source='rental.equipment.name', read_only=True)

    class Meta:
        model = RentalPayment
        fields = '__all__'
