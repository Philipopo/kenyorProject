# product_documentation/serializers.py
from rest_framework import serializers
from .models import ProductInflow, ProductOutflow, ProductSerialNumber
from django.contrib.auth import get_user_model

User = get_user_model()

class ProductSerialNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSerialNumber
        fields = ['id', 'serial_number', 'status', 'created_at']
        read_only_fields = ['created_at']

class ProductInflowSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()
    serial_numbers = ProductSerialNumberSerializer(many=True, read_only=True)
    input_serial_numbers = serializers.ListField(
        child=serializers.CharField(max_length=100), write_only=True, required=False
    )

    class Meta:
        model = ProductInflow
        fields = ['id', 'product_name', 'sku', 'production_date', 'quantity', 'cost', 'created_at', 'created_by', 'serial_numbers', 'input_serial_numbers']
        read_only_fields = ['created_at', 'created_by', 'serial_numbers']

    def validate(self, data):
        quantity = data.get('quantity')
        input_serial_numbers = data.get('input_serial_numbers', [])
        if input_serial_numbers and len(input_serial_numbers) != quantity:
            raise serializers.ValidationError("Number of serial numbers must match quantity.")
        if input_serial_numbers:
            existing = ProductSerialNumber.objects.filter(serial_number__in=input_serial_numbers).values_list('serial_number', flat=True)
            if existing:
                raise serializers.ValidationError(f"Serial numbers already exist: {', '.join(existing)}")
        return data

    def create(self, validated_data):
        input_serial_numbers = validated_data.pop('input_serial_numbers', [])
        inflow = ProductInflow.objects.create(**validated_data)
        for serial in input_serial_numbers:
            ProductSerialNumber.objects.create(inflow=inflow, serial_number=serial)
        return inflow

    def update(self, instance, validated_data):
        input_serial_numbers = validated_data.pop('input_serial_numbers', None)
        instance = super().update(instance, validated_data)
        if input_serial_numbers is not None:
            # Delete existing serial numbers and create new ones
            instance.serial_numbers.all().delete()
            for serial in input_serial_numbers:
                ProductSerialNumber.objects.create(inflow=instance, serial_number=serial)
        return instance

class ProductOutflowSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=ProductInflow.objects.all())
    responsible_staff = serializers.StringRelatedField()
    serial_numbers = ProductSerialNumberSerializer(many=True, read_only=True)
    input_serial_numbers = serializers.ListField(
        child=serializers.CharField(max_length=100), write_only=True
    )

    class Meta:
        model = ProductOutflow
        fields = ['id', 'product', 'customer_name', 'sales_order', 'dispatch_date', 'quantity', 'serial_numbers', 'input_serial_numbers', 'responsible_staff', 'created_at']
        read_only_fields = ['created_at', 'responsible_staff']

    def validate(self, data):
        quantity = data.get('quantity')
        input_serial_numbers = data.get('input_serial_numbers', [])
        product = data.get('product')
        if len(input_serial_numbers) != quantity:
            raise serializers.ValidationError("Number of serial numbers must match quantity.")
        available_serials = ProductSerialNumber.objects.filter(
            inflow=product, status='in_stock'
        ).values_list('serial_number', flat=True)
        invalid_serials = [s for s in input_serial_numbers if s not in available_serials]
        if invalid_serials:
            raise serializers.ValidationError(f"Invalid or unavailable serial numbers: {', '.join(invalid_serials)}")
        return data

    def create(self, validated_data):
        input_serial_numbers = validated_data.pop('input_serial_numbers')
        outflow = ProductOutflow.objects.create(**validated_data)
        serial_objects = ProductSerialNumber.objects.filter(serial_number__in=input_serial_numbers)
        outflow.serial_numbers.set(serial_objects)
        serial_objects.update(status='dispatched')
        return outflow

    def update(self, instance, validated_data):
        input_serial_numbers = validated_data.pop('input_serial_numbers', None)
        instance = super().update(instance, validated_data)
        if input_serial_numbers is not None:
            instance.serial_numbers.clear()
            serial_objects = ProductSerialNumber.objects.filter(serial_number__in=input_serial_numbers)
            instance.serial_numbers.set(serial_objects)
            serial_objects.update(status='dispatched')
        return instance