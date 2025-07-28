from rest_framework import serializers
from .models import Requisition, PurchaseOrder, POItem, Receiving, GoodsReceipt, Vendor

class RequisitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requisition
        fields = '__all__'
        read_only_fields = ['created_by']  # ✅ Important line


class POItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = POItem
        fields = '__all__'
        read_only_fields = ['user']


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['id', 'name', 'details', 'lead_time', 'ratings', 'document']

class PurchaseOrderSerializer(serializers.ModelSerializer):
    vendor = VendorSerializer(read_only=True)
    vendor_id = serializers.PrimaryKeyRelatedField(
        queryset=Vendor.objects.all(),
        source='vendor',
        write_only=True
    )

    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'requisition', 'vendor', 'vendor_id',
            'item_name', 'eoq', 'amount', 'date', 'status', 'notes'
        ]


class ReceivingSerializer(serializers.ModelSerializer):
    po_code = serializers.CharField(write_only=True, required=True)
    grn_code = serializers.CharField(write_only=True)
    invoice_code = serializers.CharField(write_only=True)
    attachment = serializers.FileField(write_only=True, required=False)  # <-- match 'attachment'

    class Meta:
        model = Receiving
        fields = ['id', 'po', 'po_code', 'grn', 'grn_code', 'invoice', 'invoice_code', 'attachment', 'document', 'matched', 'received_at']
        read_only_fields = ['po', 'grn', 'invoice', 'matched', 'received_at', 'document']

    def create(self, validated_data):
        po_code = validated_data.pop('po_code')
        grn_code = validated_data.pop('grn_code')
        invoice_code = validated_data.pop('invoice_code')
        attachment = validated_data.pop('attachment', None)

        try:
            po = PurchaseOrder.objects.get(code=po_code)
        except PurchaseOrder.DoesNotExist:
            raise serializers.ValidationError({'po_code': '❌ PO with this code not found.'})

        receiving = Receiving.objects.create(
            po=po,
            grn=grn_code,
            invoice=invoice_code,
            matched=True,
            document=attachment  # <-- map 'attachment' to 'document'
        )
        return receiving


class GoodsReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsReceipt
        fields = '__all__'
        read_only_fields = ['user']
