from django.db import models
from django.utils import timezone
from decimal import Decimal
from accounts.models import CustomUser
from menu.models import MenuItem

class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=255)
    apartment = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name="Apartment/Floor"
    )
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    default = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = "Addresses"
        ordering = ['-default', 'city']
    
    def __str__(self):
        if self.apartment:
            return f"{self.street_address}, {self.apartment}, {self.city}"
        return f"{self.street_address}, {self.city}"
    
    def full_address(self):
        parts = [
            self.street_address,
            self.apartment,
            self.city,
            self.phone
        ]
        return '\n'.join(filter(None, parts))

class Order(models.Model):
    PAYMENT_METHODS = [
        ('bank', 'Bank Transfer'),
        ('cash', 'Cash on Delivery'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('shipped', 'Shipped'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    canceled_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    special_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        permissions = [
            ("cancel_order", "Can cancel order"),
            ("change_status", "Can change order status"),
        ]
    
    def __str__(self):
        return f"Order #{self.id} ({self.get_status_display()})"
    
    # def save(self, *args, **kwargs):
    #     """Auto-calculate total before saving if not set"""
    #     # First save if we don't have a PK yet
    #     if not self.pk:
    #         super().save(*args, **kwargs)
            
    #     # Calculate total if needed
    #     if not self.total or kwargs.get('force_recalculate', False):
    #         self.calculate_total()
            
    #     # Save with the calculated total
    #     super().save(*args, **kwargs)
    
    def calculate_total(self):
        """Calculate total from order items"""
        self.total = Decimal('0.00')
        if self.pk:  # Only calculate if we have a PK
            for item in self.items.all():
                self.total += Decimal(str(item.price)) * Decimal(str(item.quantity))
        return self.total
    
    def cancel(self, save=True):
        if self.status == 'pending':
            self.status = 'canceled'
            self.is_active = False
            self.canceled_at = timezone.now()
            if save:
                self.save()
            return True
        return False
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('order-detail', args=[str(self.id)])

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    special_instructions = models.CharField(max_length=255, blank=True)
    
    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
    
    def __str__(self):
        return f"{self.quantity}x {self.item.name} (Order #{self.order_id})"
    
    @property
    def subtotal(self):
        return Decimal(str(self.price)) * Decimal(str(self.quantity))