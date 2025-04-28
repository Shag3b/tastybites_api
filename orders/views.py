from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Address, Order
from .serializers import AddressSerializer, OrderSerializer, CreateOrderSerializer, OrderStatusSerializer

class AddressListView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Returns only the current user's addresses"""
        return Address.objects.filter(user=self.request.user).order_by('-default', 'city')
    
    def perform_create(self, serializer):
        """Automatically sets the user"""
        serializer.save(user=self.request.user)

class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Ensures users can only access their own addresses"""
        return Address.objects.filter(user=self.request.user)

class OrderListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Uses different serializers for GET vs POST"""
        return CreateOrderSerializer if self.request.method == 'POST' else OrderSerializer
    
    def get_queryset(self):
        """Returns filtered orders with optimized queries"""
        queryset = Order.objects.filter(
            user=self.request.user
        ).select_related('address').prefetch_related('items__item')
        
        # Status filtering
        if status := self.request.query_params.get('status'):
            queryset = queryset.filter(status=status)
        
        # Hide canceled unless requested
        if self.request.query_params.get('show_canceled', 'false').lower() != 'true':
            queryset = queryset.exclude(status='canceled')
            
        return queryset.order_by('-created_at')

class OrderDetailView(generics.RetrieveUpdateAPIView):  # Changed to support updates
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Secure queryset with user filter and optimizations"""
        return Order.objects.filter(
            user=self.request.user
        ).select_related('address').prefetch_related('items__item')

class OrderStatusView(generics.UpdateAPIView):
    """For updating order status (e.g., preparing -> shipped)"""
    serializer_class = OrderStatusSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class OrderCancelView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        """Handles order cancellation with validation"""
        order = get_object_or_404(Order, pk=pk, user=request.user)
        
        if order.status != 'pending':
            return Response(
                {'error': 'Only pending orders can be canceled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.cancel()  # Using the model method we created
        
        return Response(
            OrderSerializer(order, context={'request': request}).data,
            status=status.HTTP_200_OK
        )