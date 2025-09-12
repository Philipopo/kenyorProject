from rest_framework import serializers
from .models import Equipment, Rental, RentalPayment

class EquipmentSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True, default='N/A')

    class Meta:
        model = Equipment
        fields = ['id', 'name', 'category', 'condition', 'location', 'created_by', 'created_at', 'created_by_name']
        read_only_fields = ['created_by', 'created_at', 'created_by_name']

    def validate(self, data):
        if not data.get('name') or not data.get('category') or not data.get('condition') or not data.get('location'):
            raise serializers.ValidationError('All fields are required.')
        return data

class RentalSerializer(serializers.ModelSerializer):
    renter_name = serializers.CharField(source='renter.full_name', read_only=True, default='N/A')
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True, default='N/A')

    class Meta:
        model = Rental
        fields = ['id', 'code', 'renter', 'renter_name', 'equipment', 'equipment_name', 'start_date', 'due_date', 'status', 'created_by', 'created_at', 'created_by_name']
        read_only_fields = ['id', 'code', 'renter', 'created_by', 'created_at', 'created_by_name', 'renter_name', 'equipment_name']

    def validate(self, data):
        if data.get('start_date') > data.get('due_date'):
            raise serializers.ValidationError({'due_date': 'Due date must be after start date.'})
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['renter'] = request.user
            validated_data['created_by'] = request.user
        return super().create(validated_data)


        

class RentalPaymentSerializer(serializers.ModelSerializer):
    renter_name = serializers.CharField(source='rental.renter.full_name', read_only=True, default='N/A')
    equipment_name = serializers.CharField(source='rental.equipment.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True, default='N/A')

    class Meta:
        model = RentalPayment
        fields = ['id', 'rental', 'renter_name', 'equipment_name', 'amount_paid', 'payment_date', 'status', 'created_by', 'created_at', 'created_by_name']
        read_only_fields = ['payment_date', 'created_by', 'created_at', 'created_by_name']

    def validate(self, data):
        if data.get('amount_paid', 0) <= 0:
            raise serializers.ValidationError({'amount_paid': 'Amount paid must be positive.'})
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        return super().create(validated_data)