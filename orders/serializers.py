from rest_framework import serializers
from .models import Address, Order, OrderItem, Address
from menu.serializers import MenuItemSerializer
from menu.models import MenuItem
from decimal import Decimal

### ----- Address Serializer -----
class AddressSerializer(serializers.ModelSerializer):
    full_address = serializers.SerializerMethodField()

    class Meta:
        model = Address
        fields = (
            'id', 'street_address', 'apartment', 'city',
            'phone', 'default', 'full_address'
        )

    def get_full_address(self, obj):
        parts = [obj.street_address]
        if obj.apartment:
            parts.append(obj.apartment)
        parts.append(obj.city)
        return ', '.join(parts)


### ----- Read-Only OrderItem Serializer (with nested MenuItem) -----
class OrderItemSerializer(serializers.ModelSerializer):
    item = MenuItemSerializer()
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = (
            'id', 'item', 'quantity', 'price', 'subtotal', 'special_instructions'
        )
        read_only_fields = ('price', 'subtotal')

    def get_subtotal(self, obj):
        return Decimal(str(obj.price)) * Decimal(str(obj.quantity))


### ----- Order Status Serializer (for PATCH status updates) -----
class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'status')
        read_only_fields = ('id',)


### ----- Full Order Serializer (for retrieval) -----
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    address = AddressSerializer()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    can_cancel = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id', 'user', 'address', 'created_at', 'updated_at',
            'payment_method', 'total', 'status', 'status_display',
            'canceled_at', 'is_active', 'special_notes', 'items', 'can_cancel'
        )
        read_only_fields = (
            'user', 'created_at', 'updated_at', 'canceled_at', 'total'
        )

    def get_can_cancel(self, obj):
        return obj.status == 'pending'


### ----- Create-Only OrderItem (flat input, not nested) -----
class CreateOrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ('item', 'quantity', 'special_instructions')
        

# orders/serializers.py

class CreateOrderSerializer(serializers.ModelSerializer):
    items = CreateOrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ('address', 'payment_method', 'items', 'special_notes')

    def create(self, validated_data):
        items_data = validated_data.pop('items')

        # 1) INSERT the Order (total starts at zero)
        order = Order.objects.create(
            user=self.context['request'].user,
            **validated_data,
            status='pending',
            total=Decimal('0.00')
        )

        # 2) INSERT all OrderItems
        for item_data in items_data:
            OrderItem.objects.create(
                order=order,
                item=item_data['item'],
                quantity=item_data['quantity'],
                price=item_data['item'].price,
                special_instructions=item_data.get('special_instructions', '')
            )

        # 3) calculate_total (uses self.pk guard) and then do an UPDATE
        order.total = order.calculate_total()
        order.save(update_fields=['total'])

        return order
