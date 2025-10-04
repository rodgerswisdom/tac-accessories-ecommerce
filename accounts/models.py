from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Customer Profile'
        verbose_name_plural = 'Customer Profiles'

    def __str__(self):
        return f"{self.user.get_full_name()} Profile"

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

class CustomerAddress(models.Model):
    ADDRESS_TYPE_CHOICES = [
        ('billing', 'Billing'),
        ('shipping', 'Shipping'),
        ('both', 'Both'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES, default='shipping')
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    line1 = models.CharField(max_length=120, verbose_name='Address Line 1')
    line2 = models.CharField(max_length=120, blank=True, verbose_name='Address Line 2')
    city = models.CharField(max_length=60)
    postal_code = models.CharField(max_length=20, blank=True)
    county = models.CharField(max_length=60, default='Nairobi')
    country = models.CharField(max_length=60, default='Kenya')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Customer Address'
        verbose_name_plural = 'Customer Addresses'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.line1}, {self.city}"

    def save(self, *args, **kwargs):
        # Ensure only one default address per customer per type
        if self.is_default:
            CustomerAddress.objects.filter(
                customer=self.customer,
                address_type=self.address_type
            ).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)

# Signal to create profile when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        CustomerProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
