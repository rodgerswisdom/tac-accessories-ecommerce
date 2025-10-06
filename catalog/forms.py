from django import forms
from django.core.exceptions import ValidationError
from .models import Product, Category, Tag
import re

class ProductForm(forms.ModelForm):
    """Comprehensive product creation form with validation"""
    
    # Basic Information
    name = forms.CharField(
        max_length=120,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gold-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Enter product name (e.g., Gold Diamond Ring)'
        }),
        help_text="Enter a descriptive name for your product"
    )
    
    short_description = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gold-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Brief description (e.g., Elegant 18K gold ring with diamond)'
        }),
        help_text="Short description for product listings"
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gold-500 focus:border-transparent transition-all duration-200',
            'rows': 4,
            'placeholder': 'Detailed product description...'
        }),
        help_text="Detailed description of the product"
    )
    
    # Category and Tags
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        empty_label="Select a category",
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gold-500 focus:border-transparent transition-all duration-200'
        })
    )
    
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.filter(is_active=True),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'space-y-2'
        }),
        help_text="Select relevant tags for this product"
    )
    
    # Pricing
    price_cents = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gold-500 focus:border-transparent transition-all duration-200',
            'placeholder': '0',
            'step': '1'
        }),
        help_text="Price in cents (e.g., 50000 for KES 500.00)"
    )
    
    compare_price_cents = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gold-500 focus:border-transparent transition-all duration-200',
            'placeholder': '0',
            'step': '1'
        }),
        help_text="Original price for showing discounts (optional)"
    )
    
    # Inventory
    sku = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gold-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Auto-generated if left empty'
        }),
        help_text="Stock Keeping Unit (leave empty for auto-generation)"
    )
    
    stock_quantity = forms.IntegerField(
        min_value=0,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gold-500 focus:border-transparent transition-all duration-200',
            'placeholder': '0'
        })
    )
    
    low_stock_threshold = forms.IntegerField(
        min_value=0,
        initial=5,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gold-500 focus:border-transparent transition-all duration-200',
            'placeholder': '5'
        }),
        help_text="Alert when stock falls below this number"
    )
    
    weight_grams = forms.IntegerField(
        min_value=0,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gold-500 focus:border-transparent transition-all duration-200',
            'placeholder': '0'
        }),
        help_text="Weight in grams for shipping calculations"
    )
    
    # Jewellery Specific
    material = forms.ChoiceField(
        choices=Product.MATERIAL_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gold-500 focus:border-transparent transition-all duration-200'
        })
    )
    
    carat = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gold-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'e.g., 18K, 24K, 925'
        }),
        help_text="Gold carat or silver purity"
    )
    
    stone_type = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gold-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'e.g., Diamond, Ruby, Emerald'
        }),
        help_text="Type of stone used"
    )
    
    stone_count = forms.IntegerField(
        min_value=0,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gold-500 focus:border-transparent transition-all duration-200',
            'placeholder': '0'
        }),
        help_text="Number of stones"
    )
    
    size = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gold-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'e.g., Size 7, 18 inches, Medium'
        }),
        help_text="Ring size, chain length, or other size specification"
    )
    
    # Images
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'hidden',
            'accept': 'image/*'
        }),
        help_text="Main product image"
    )
    
    
    # Status
    is_featured = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-gold-600 bg-gray-100 border-gray-300 rounded focus:ring-gold-500 focus:ring-2'
        })
    )
    
    is_new = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-gold-600 bg-gray-100 border-gray-300 rounded focus:ring-gold-500 focus:ring-2'
        })
    )
    
    is_bestseller = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-gold-600 bg-gray-100 border-gray-300 rounded focus:ring-gold-500 focus:ring-2'
        })
    )
    
    track_inventory = forms.BooleanField(
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-gold-600 bg-gray-100 border-gray-300 rounded focus:ring-gold-500 focus:ring-2'
        })
    )

    class Meta:
        model = Product
        fields = [
            'name', 'short_description', 'description', 'category', 'tags',
            'price_cents', 'compare_price_cents', 'sku', 'stock_quantity',
            'low_stock_threshold', 'weight_grams', 'material', 'carat',
            'stone_type', 'stone_count', 'size', 'image',
            'is_featured', 'is_new', 'is_bestseller', 'track_inventory'
        ]

    def clean_price_cents(self):
        price = self.cleaned_data.get('price_cents')
        if price and price < 1:
            raise ValidationError("Price must be greater than 0.")
        return price

    def clean_compare_price_cents(self):
        compare_price = self.cleaned_data.get('compare_price_cents')
        price = self.cleaned_data.get('price_cents')
        
        if compare_price and price and compare_price <= price:
            raise ValidationError("Compare price must be greater than the regular price.")
        return compare_price

    def clean_carat(self):
        carat = self.cleaned_data.get('carat')
        if carat:
            # Basic validation for carat format
            if not re.match(r'^[0-9]+[Kk]?$', carat.strip()):
                raise ValidationError("Please enter a valid carat format (e.g., 18K, 24K, 925).")
        return carat

    def clean_sku(self):
        sku = self.cleaned_data.get('sku')
        if sku:
            # Check if SKU already exists
            if Product.objects.filter(sku=sku).exists():
                raise ValidationError("A product with this SKU already exists.")
        return sku

    def clean(self):
        cleaned_data = super().clean()
        
        # Additional cross-field validation
        material = cleaned_data.get('material')
        carat = cleaned_data.get('carat')
        
        # If material is gold or silver, carat is recommended
        if material in ['gold', 'silver'] and not carat:
            self.add_error('carat', f"For {material} products, please specify the carat/purity.")
        
        return cleaned_data
