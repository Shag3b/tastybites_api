# Create your views here.
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Address, Order
from .serializers import AddressSerializer, OrderSerializer, CreateOrderSerializer
from accounts.models import CustomUser

class AddressListView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

class OrderListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        return OrderSerializer
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Calculate total
        items_data = serializer.validated_data['items']
        total = sum(item['item'].price * item['quantity'] for item in items_data)
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            address=serializer.validated_data['address'],
            payment_method=serializer.validated_data['payment_method'],
            total=total
        )
        
        # Create order items
        for item_data in items_data:
            order.items.create(
                item=item_data['item'],
                quantity=item_data['quantity'],
                price=item_data['item'].price
            )
        
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)