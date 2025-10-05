from django.db import models
from django.utils.text import slugify
import uuid
from decimal import Decimal

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
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class ProductImage(models.Model):
    """Product gallery images"""
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='products/gallery/')
    is_main = models.BooleanField(default=False, help_text="Mark as main product image")
    alt_text = models.CharField(max_length=255, blank=True, help_text="Alt text for accessibility")
    sort_order = models.PositiveIntegerField(default=0, help_text="Order for displaying images")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'created_at']
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'

    def __str__(self):
        return f"{self.product.name} - Image {self.id}"

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
    
    # Images - keeping main image field for backward compatibility
    image = models.ImageField(upload_to='products/main/', blank=True, null=True, help_text="Main product image")
    thumbnail = models.ImageField(upload_to='products/thumbnails/', blank=True, null=True, help_text="Product thumbnail")
    
    # Status fields
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_new = models.BooleanField(default=False, help_text="Mark as new arrival")
    is_bestseller = models.BooleanField(default=False, help_text="Mark as bestseller")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

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

    @property
    def all_images(self):
        """Return all product images as a list"""
        images = []
        if self.image:
            images.append(self.image.url)
        # Add gallery images from the related ProductImage model
        for gallery_image in self.gallery_images.all():
            images.append(gallery_image.image.url)
        return images

    @property
    def has_images(self):
        """Check if product has any images"""
        return bool(self.image or self.gallery_images.exists())

    @property
    def primary_image(self):
        """Return the primary image URL or None"""
        if self.image:
            return self.image.url
        # Check for main gallery image
        main_gallery_image = self.gallery_images.filter(is_main=True).first()
        if main_gallery_image:
            return main_gallery_image.image.url
        # Fallback to first gallery image
        first_gallery_image = self.gallery_images.first()
        if first_gallery_image:
            return first_gallery_image.image.url
        return None

    def get_gallery_images(self):
        """Get all gallery images ordered by sort_order"""
        return self.gallery_images.all().order_by('sort_order', 'created_at')


class ProductPrice(models.Model):
    """Regional pricing for products"""
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('KES', 'Kenyan Shilling'),
        ('NGN', 'Nigerian Naira'),
        ('ZAR', 'South African Rand'),
        ('GHS', 'Ghanaian Cedi'),
        ('EGP', 'Egyptian Pound'),
        ('MAD', 'Moroccan Dirham'),
        ('TND', 'Tunisian Dinar'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='regional_prices')
    country_code = models.CharField(max_length=2, help_text="ISO 3166-1 alpha-2 country code")
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    price_cents = models.PositiveIntegerField(help_text="Price in minor currency units (cents)")
    is_override = models.BooleanField(default=True, help_text="If True, use this exact price. If False, use as multiplier for base price.")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['product', 'country_code', 'currency']
        ordering = ['country_code', 'currency']
        verbose_name = 'Product Price'
        verbose_name_plural = 'Product Prices'

    def __str__(self):
        return f"{self.product.name} - {self.country_code} ({self.currency})"

    @property
    def price_display(self) -> str:
        return f"{self.currency} {self.price_cents / 100:,.2f}"


class CurrencyRate(models.Model):
    """Exchange rates for currency conversion"""
    from_currency = models.CharField(max_length=3, choices=ProductPrice.CURRENCY_CHOICES)
    to_currency = models.CharField(max_length=3, choices=ProductPrice.CURRENCY_CHOICES)
    rate = models.DecimalField(max_digits=10, decimal_places=6, help_text="Exchange rate from_currency to to_currency")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['from_currency', 'to_currency']
        ordering = ['from_currency', 'to_currency']
        verbose_name = 'Currency Rate'
        verbose_name_plural = 'Currency Rates'

    def __str__(self):
        return f"{self.from_currency} to {self.to_currency}: {self.rate}"

    @classmethod
    def get_rate(cls, from_currency: str, to_currency: str) -> Decimal:
        """Get exchange rate between two currencies"""
        if from_currency == to_currency:
            return Decimal('1.0')
        
        try:
            rate = cls.objects.get(
                from_currency=from_currency,
                to_currency=to_currency,
                is_active=True
            )
            return rate.rate
        except cls.DoesNotExist:
            # Try reverse rate
            try:
                reverse_rate = cls.objects.get(
                    from_currency=to_currency,
                    to_currency=from_currency,
                    is_active=True
                )
                return Decimal('1.0') / reverse_rate.rate
            except cls.DoesNotExist:
                # Default to 1.0 if no rate found
                return Decimal('1.0')