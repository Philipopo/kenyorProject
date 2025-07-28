from rest_framework import serializers
from .models import Receipt, StockReceipt, SigningReceipt

class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = '__all__'

class StockReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockReceipt
        fields = '__all__'

class SigningReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = SigningReceipt
        fields = '__all__'
