from rest_framework import serializers
from .models import Address, Order, OrderItem
from menu.serializers import MenuItemSerializer

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('id', 'street_address', 'apartment', 'city', 'phone', 'default')

class OrderItemSerializer(serializers.ModelSerializer):
    item = MenuItemSerializer()
    
    class Meta:
        model = OrderItem
        fields = ('id', 'item', 'quantity', 'price')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    address = AddressSerializer()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = ('id', 'user', 'address', 'created_at', 'payment_method', 
                 'total', 'status', 'status_display', 'canceled_at', 'items')

class CreateOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('item', 'quantity')

class CreateOrderSerializer(serializers.ModelSerializer):
    items = CreateOrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = ('address', 'payment_method', 'items')
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(
            **validated_data,
            user=self.context['request'].user,
            status='pending'
        )
        
        # Calculate and set total
        total = sum(item['item'].price * item['quantity'] for item in items_data)
        order.total = total
        order.save()
        
        # Create order items
        for item_data in items_data:
            OrderItem.objects.create(
                order=order,
                item=item_data['item'],
                quantity=item_data['quantity'],
                price=item_data['item'].price
            )
        
        return order