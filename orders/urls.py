from django.urls import path
from .views import AddressListView, AddressDetailView, OrderListView, OrderDetailView

urlpatterns = [
    path('addresses/', AddressListView.as_view(), name='address_list'),
    path('addresses/<int:pk>/', AddressDetailView.as_view(), name='address_detail'),
    path('', OrderListView.as_view(), name='order_list'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
]