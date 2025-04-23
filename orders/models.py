from django.db import models

from accounts.models import CustomUser
from menu.models import MenuItem

class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=255)
    apartment = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    default = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.street_address}, {self.city}"

class Order(models.Model):
    PAYMENT_METHODS = [
        ('bank', 'Bank Transfer'),
        ('cash', 'Cash on Delivery'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Order #{self.id} by {self.user.email}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity}x {self.item.name} for order #{self.order.id}"
