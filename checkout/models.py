from django.db import models

class Address(models.Model):
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    line1 = models.CharField(max_length=120)
    line2 = models.CharField(max_length=120, blank=True)
    city = models.CharField(max_length=60)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    address = models.ForeignKey(Address, on_delete=models.PROTECT)
    total_cents = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, default="pending")