from django.db import models
from django.utils.text import slugify
import uuid

class Tag(models.Model):
    """Tags for jewellery items (e.g., gold, silver, diamond, etc.)"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True)
    color = models.CharField(max_length=7, default='#FFD700', help_text='Hex color for tag display')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Category(models.Model):
    """Categories for jewellery (e.g., Rings, Necklaces, etc.)"""
    GENDER_CHOICES = [
        ('unisex', 'Unisex'),
        ('men', 'Men'),
        ('women', 'Women'),
    ]
    
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='unisex')
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Product(models.Model):
    """Jewellery products with enhanced fields"""
    MATERIAL_CHOICES = [
        ('gold', 'Gold'),
        ('silver', 'Silver'),
        ('platinum', 'Platinum'),
        ('diamond', 'Diamond'),
        ('gemstone', 'Gemstone'),
        ('pearl', 'Pearl'),
        ('other', 'Other'),
    ]
    
    category = models.ForeignKey(Category, related_name="products", on_delete=models.PROTECT)
    tags = models.ManyToManyField(Tag, blank=True, related_name='products')
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=130, unique=True)
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=255, blank=True)
    price_cents = models.PositiveIntegerField()
    compare_price_cents = models.PositiveIntegerField(null=True, blank=True, help_text="Original price for showing discounts")
    sku = models.CharField(max_length=50, unique=True, blank=True, help_text="Stock Keeping Unit")
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    track_inventory = models.BooleanField(default=True)
    weight_grams = models.PositiveIntegerField(default=0, help_text="Weight in grams for shipping calculations")
    
    # Jewellery specific fields
    material = models.CharField(max_length=20, choices=MATERIAL_CHOICES, default='gold')
    carat = models.CharField(max_length=10, blank=True, help_text="Gold carat (e.g., 18K, 24K)")
    stone_type = models.CharField(max_length=50, blank=True, help_text="Type of stone (diamond, ruby, etc.)")
    stone_count = models.PositiveIntegerField(default=0, help_text="Number of stones")
    size = models.CharField(max_length=20, blank=True, help_text="Ring size, chain length, etc.")
    
    # Images
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='products/thumbnails/', blank=True, null=True)
    gallery_images = models.JSONField(default=list, blank=True, help_text="Additional product images")
    
    # Status fields
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_new = models.BooleanField(default=False, help_text="Mark as new arrival")
    is_bestseller = models.BooleanField(default=False, help_text="Mark as bestseller")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.sku:
            self.sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    @property
    def price_display(self) -> str:
        return f"KES {self.price_cents / 100:,.2f}"

    @property
    def compare_price_display(self) -> str:
        if self.compare_price_cents:
            return f"KES {self.compare_price_cents / 100:,.2f}"
        return None

    @property
    def in_stock(self):
        if not self.track_inventory:
            return True
        return self.stock_quantity > 0

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.low_stock_threshold

    @property
    def discount_percentage(self):
        if self.compare_price_cents and self.compare_price_cents > self.price_cents:
            return int(((self.compare_price_cents - self.price_cents) / self.compare_price_cents) * 100)
        return 0