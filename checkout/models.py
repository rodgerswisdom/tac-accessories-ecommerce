from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class Address(models.Model):
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    line1 = models.CharField(max_length=120)
    line2 = models.CharField(max_length=120, blank=True)
    city = models.CharField(max_length=60)
    county = models.CharField(max_length=60)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=60)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Order Address'
        verbose_name_plural = 'Order Addresses'

    def __str__(self):
        return f"{self.full_name} - {self.line1}, {self.city}"

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('mpesa', 'M-Pesa'),
        ('card', 'Credit/Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
    ]

    # Basic order info
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Address information
    address = models.ForeignKey(Address, on_delete=models.PROTECT)
    
    # Order status and tracking
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cod')
    
    # Financial information
    subtotal_cents = models.PositiveIntegerField(default=0)
    shipping_cost_cents = models.PositiveIntegerField(default=0)
    tax_cents = models.PositiveIntegerField(default=0)
    total_cents = models.PositiveIntegerField(default=0)
    
    # Additional information
    notes = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True, help_text="Internal notes for staff")
    
    # Tracking dates
    confirmed_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"Order #{self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    def generate_order_number(self):
        """Generate a unique order number"""
        timestamp = timezone.now().strftime('%Y%m%d')
        unique_id = str(uuid.uuid4().hex[:6].upper())
        return f"ORD-{timestamp}-{unique_id}"

    @property
    def total_display(self):
        return f"KES {self.total_cents / 100:,.2f}"

    @property
    def subtotal_display(self):
        return f"KES {self.subtotal_cents / 100:,.2f}"

    @property
    def shipping_display(self):
        return f"KES {self.shipping_cost_cents / 100:,.2f}"

    @property
    def tax_display(self):
        return f"KES {self.tax_cents / 100:,.2f}"

    def calculate_totals(self):
        """Calculate order totals from order items"""
        self.subtotal_cents = sum(item.total_cents for item in self.items.all())
        # Add shipping and tax calculations here if needed
        self.total_cents = self.subtotal_cents + self.shipping_cost_cents + self.tax_cents
        self.save(update_fields=['subtotal_cents', 'total_cents'])

    def can_be_cancelled(self):
        """Check if order can be cancelled"""
        return self.status in ['pending', 'confirmed', 'processing']

    def cancel_order(self, reason=None):
        """Cancel the order"""
        if self.can_be_cancelled():
            self.status = 'cancelled'
            self.cancelled_at = timezone.now()
            if reason:
                self.internal_notes += f"\nCancelled: {reason}"
            self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('catalog.Product', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price_cents = models.PositiveIntegerField(help_text="Price at time of order")
    total_cents = models.PositiveIntegerField(help_text="quantity * price_cents")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        unique_together = ['order', 'product']

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def save(self, *args, **kwargs):
        self.total_cents = self.quantity * self.price_cents
        super().save(*args, **kwargs)
        # Recalculate order totals
        self.order.calculate_totals()

    @property
    def price_display(self):
        return f"KES {self.price_cents / 100:,.2f}"

    @property
    def total_display(self):
        return f"KES {self.total_cents / 100:,.2f}"