from rest_framework import serializers
from .models import Address, Order, OrderItem
from menu.serializers import MenuItemSerializer

class AddressSerializer(serializers.ModelSerializer):
    full_address = serializers.SerializerMethodField()
    
    class Meta:
        model = Address
        fields = ('id', 'street_address', 'apartment', 'city', 'phone', 'default', 'full_address')
    
    def get_full_address(self, obj):
        parts = [obj.street_address]
        if obj.apartment:
            parts.append(obj.apartment)
        parts.append(obj.city)
        return ', '.join(parts)

class OrderItemSerializer(serializers.ModelSerializer):
    item = MenuItemSerializer()
    subtotal = serializers.DecimalField(
        source='price',
        max_digits=6,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = OrderItem
        fields = ('id', 'item', 'quantity', 'price', 'subtotal', 'special_instructions')

class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'status')
        read_only_fields = ('id',)

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
        read_only_fields = ('user', 'created_at', 'updated_at', 'canceled_at')
    
    def get_can_cancel(self, obj):
        return obj.status == 'pending'

class CreateOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('item', 'quantity', 'special_instructions')
        extra_kwargs = {
            'special_instructions': {'required': False, 'allow_blank': True}
        }

class CreateOrderSerializer(serializers.ModelSerializer):
    items = CreateOrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = ('address', 'payment_method', 'items', 'special_notes')
        extra_kwargs = {
            'special_notes': {'required': False, 'allow_blank': True}
        }
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        special_notes = validated_data.pop('special_notes', '')
        
        order = Order.objects.create(
            **validated_data,
            user=self.context['request'].user,
            status='pending',
            special_notes=special_notes
        )
        
        # Calculate total and create items
        total = 0
        for item_data in items_data:
            item_price = item_data['item'].price
            quantity = item_data['quantity']
            total += item_price * quantity
            
            OrderItem.objects.create(
                order=order,
                item=item_data['item'],
                quantity=quantity,
                price=item_price,
                special_instructions=item_data.get('special_instructions', '')
            )
        
        order.total = total
        order.save()
        return order