from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from catalog.models import Category, Product
from accounts.models import CustomerProfile, CustomerAddress
from checkout.models import Order, OrderItem, Address


class UserSerializer(serializers.ModelSerializer):
    """User serializer for registration and profile management"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password', 'password_confirm')
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Login serializer"""
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include username and password')


class CustomerProfileSerializer(serializers.ModelSerializer):
    """Customer profile serializer"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = CustomerProfile
        fields = ('id', 'user', 'phone', 'date_of_birth', 'gender', 'avatar', 
                 'email_verified', 'phone_verified', 'created_at', 'updated_at')
        read_only_fields = ('email_verified', 'phone_verified', 'created_at', 'updated_at')


class CustomerAddressSerializer(serializers.ModelSerializer):
    """Customer address serializer"""
    
    class Meta:
        model = CustomerAddress
        fields = ('id', 'address_type', 'full_name', 'phone', 'line1', 'line2', 
                 'city', 'postal_code', 'county', 'country', 'is_default', 
                 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
    
    def validate(self, attrs):
        # Ensure only one default address per type per customer
        if attrs.get('is_default'):
            customer = self.context['request'].user
            address_type = attrs.get('address_type')
            
            # Exclude current instance if updating
            queryset = CustomerAddress.objects.filter(
                customer=customer,
                address_type=address_type,
                is_default=True
            )
            if self.instance:
                queryset = queryset.exclude(id=self.instance.id)
            
            if queryset.exists():
                queryset.update(is_default=False)
        
        return attrs


class CategorySerializer(serializers.ModelSerializer):
    """Category serializer"""
    product_count = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'image', 'parent', 
                 'is_active', 'sort_order', 'product_count', 'children', 
                 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
    
    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()
    
    def get_children(self, obj):
        children = obj.children.filter(is_active=True).order_by('sort_order', 'name')
        return CategorySerializer(children, many=True, context=self.context).data


class ProductSerializer(serializers.ModelSerializer):
    """Product serializer"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    discount_percentage = serializers.ReadOnlyField()
    stock_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'description', 'short_description', 
                 'price_cents', 'compare_price_cents', 'sku', 'stock_quantity', 
                 'low_stock_threshold', 'track_inventory', 'weight_grams', 
                 'image', 'thumbnail', 'is_featured', 'is_active', 'in_stock',
                 'category', 'category_name', 'category_slug', 'discount_percentage',
                 'stock_status', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at', 'sku')
    
    def get_stock_status(self, obj):
        if not obj.track_inventory:
            return 'unlimited'
        elif obj.stock_quantity == 0:
            return 'out_of_stock'
        elif obj.is_low_stock:
            return 'low_stock'
        else:
            return 'in_stock'


class ProductListSerializer(ProductSerializer):
    """Simplified product serializer for list views"""
    class Meta(ProductSerializer.Meta):
        fields = ('id', 'name', 'slug', 'short_description', 'price_cents', 
                 'compare_price_cents', 'sku', 'stock_quantity', 'image', 
                 'thumbnail', 'is_featured', 'is_active', 'in_stock',
                 'category_name', 'category_slug', 'discount_percentage',
                 'stock_status', 'created_at')


class OrderAddressSerializer(serializers.ModelSerializer):
    """Order address serializer"""
    
    class Meta:
        model = Address
        fields = ('id', 'full_name', 'phone', 'line1', 'line2', 'city', 
                 'county', 'postal_code', 'country', 'notes', 'created_at')


class OrderItemSerializer(serializers.ModelSerializer):
    """Order item serializer"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'product_sku', 'product_image',
                 'quantity', 'price_cents', 'total_cents', 'created_at')
        read_only_fields = ('total_cents', 'created_at')
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value


class OrderSerializer(serializers.ModelSerializer):
    """Order serializer"""
    items = OrderItemSerializer(many=True, read_only=True)
    address = OrderAddressSerializer(read_only=True)
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    customer_email = serializers.CharField(source='customer.email', read_only=True)
    total_display = serializers.ReadOnlyField()
    subtotal_display = serializers.ReadOnlyField()
    shipping_display = serializers.ReadOnlyField()
    tax_display = serializers.ReadOnlyField()
    
    class Meta:
        model = Order
        fields = ('id', 'order_number', 'customer', 'customer_name', 'customer_email',
                 'address', 'status', 'payment_status', 'payment_method',
                 'subtotal_cents', 'shipping_cost_cents', 'tax_cents', 'total_cents',
                 'subtotal_display', 'shipping_display', 'tax_display', 'total_display',
                 'notes', 'internal_notes', 'items', 'created_at', 'updated_at',
                 'confirmed_at', 'shipped_at', 'delivered_at', 'cancelled_at')
        read_only_fields = ('order_number', 'created_at', 'updated_at', 'customer',
                           'confirmed_at', 'shipped_at', 'delivered_at', 'cancelled_at')


class OrderCreateSerializer(serializers.ModelSerializer):
    """Order creation serializer"""
    items = OrderItemSerializer(many=True)
    address = OrderAddressSerializer()
    
    class Meta:
        model = Order
        fields = ('address', 'payment_method', 'notes', 'items')
    
    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Order must have at least one item")
        
        for item in value:
            product = item['product']
            quantity = item['quantity']
            
            # Check if product is active
            if not product.is_active:
                raise serializers.ValidationError(f"Product {product.name} is not available")
            
            # Check stock availability
            if product.track_inventory and product.stock_quantity < quantity:
                raise serializers.ValidationError(
                    f"Insufficient stock for {product.name}. Available: {product.stock_quantity}"
                )
        
        return value
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        address_data = validated_data.pop('address')
        
        # Create address
        address = Address.objects.create(**address_data)
        
        # Create order
        order = Order.objects.create(
            address=address,
            customer=self.context['request'].user if self.context['request'].user.is_authenticated else None,
            **validated_data
        )
        
        # Create order items and calculate totals
        total_cents = 0
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            price_cents = product.price_cents
            
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price_cents=price_cents
            )
            
            total_cents += price_cents * quantity
            
            # Update product stock
            if product.track_inventory:
                product.stock_quantity -= quantity
                product.save(update_fields=['stock_quantity'])
        
        # Update order totals
        order.subtotal_cents = total_cents
        order.total_cents = total_cents + order.shipping_cost_cents + order.tax_cents
        order.save(update_fields=['subtotal_cents', 'total_cents'])
        
        return order


class CartItemSerializer(serializers.Serializer):
    """Cart item serializer for session-based cart"""
    product_id = serializers.IntegerField()
    product_name = serializers.CharField(read_only=True)
    product_slug = serializers.CharField(read_only=True)
    product_image = serializers.ImageField(read_only=True)
    price_cents = serializers.IntegerField(read_only=True)
    quantity = serializers.IntegerField(min_value=1)
    total_cents = serializers.IntegerField(read_only=True)
    
    def validate_product_id(self, value):
        try:
            product = Product.objects.get(id=value, is_active=True)
            if product.track_inventory and product.stock_quantity <= 0:
                raise serializers.ValidationError("Product is out of stock")
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")


class CartSerializer(serializers.Serializer):
    """Cart serializer"""
    items = CartItemSerializer(many=True)
    total_items = serializers.IntegerField(read_only=True)
    total_cents = serializers.IntegerField(read_only=True)
    total_display = serializers.CharField(read_only=True)
