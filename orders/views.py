from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Address, Order
from .serializers import AddressSerializer, OrderSerializer, CreateOrderSerializer

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
        return CreateOrderSerializer if self.request.method == 'POST' else OrderSerializer
    
    def get_queryset(self):
        queryset = Order.objects.filter(user=self.request.user)
        
        # Status filtering
        if status := self.request.query_params.get('status'):
            queryset = queryset.filter(status=status)
        
        # Hide canceled unless requested
        if self.request.query_params.get('show_canceled', 'false').lower() != 'true':
            queryset = queryset.exclude(status='canceled')
            
        return queryset.order_by('-created_at')

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class OrderCancelView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        
        if order.status != 'pending':
            return Response(
                {'error': 'Only pending orders can be canceled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'canceled'
        order.canceled_at = timezone.now()
        order.save()
        
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_200_OK
        )