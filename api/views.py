from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models import Q, F
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django.core.cache import cache
from django.conf import settings

from catalog.models import Category, Product
from accounts.models import CustomerProfile, CustomerAddress
from checkout.models import Order, OrderItem
from .serializers import (
    UserSerializer, UserLoginSerializer, CustomerProfileSerializer,
    CustomerAddressSerializer, CategorySerializer, ProductSerializer,
    ProductListSerializer, OrderSerializer, OrderCreateSerializer,
    CartItemSerializer, CartSerializer
)


class UserRegistrationView(APIView):
    """User registration endpoint"""
    permission_classes = [permissions.AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='10/m', method='POST'))
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(TokenObtainPairView):
    """User login endpoint with rate limiting"""
    permission_classes = [permissions.AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='20/m', method='POST'))
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """User profile management"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            profile = request.user.profile
            serializer = CustomerProfileSerializer(profile)
            return Response(serializer.data)
        except CustomerProfile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request):
        try:
            profile = request.user.profile
            serializer = CustomerProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CustomerProfile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Category viewset"""
    queryset = Category.objects.filter(is_active=True).order_by('sort_order', 'name')
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'sort_order', 'created_at']
    ordering = ['sort_order', 'name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Include parent categories for hierarchical display
        if self.action == 'list':
            queryset = queryset.filter(parent__isnull=True)
        return queryset


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """Product viewset"""
    queryset = Product.objects.filter(is_active=True).select_related('category')
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_featured', 'track_inventory']
    search_fields = ['name', 'description', 'short_description', 'sku', 'category__name']
    ordering_fields = ['name', 'price_cents', 'created_at', 'stock_quantity']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category slug
        category_slug = self.request.query_params.get('category_slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price_cents__gte=int(min_price) * 100)
        if max_price:
            queryset = queryset.filter(price_cents__lte=int(max_price) * 100)
        
        # Filter by stock status
        in_stock = self.request.query_params.get('in_stock')
        if in_stock and in_stock.lower() == 'true':
            queryset = queryset.filter(
                Q(track_inventory=False) | Q(stock_quantity__gt=0)
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products"""
        featured_products = self.get_queryset().filter(is_featured=True)
        serializer = self.get_serializer(featured_products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Enhanced search endpoint"""
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response({'error': 'Search query is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Cache search results for 5 minutes
        cache_key = f"product_search_{hash(query)}"
        cached_results = cache.get(cache_key)
        
        if cached_results is None:
            products = self.get_queryset().filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(short_description__icontains=query) |
                Q(sku__icontains=query) |
                Q(category__name__icontains=query)
            )
            serializer = self.get_serializer(products, many=True)
            cached_results = serializer.data
            cache.set(cache_key, cached_results, 300)  # 5 minutes
        
        return Response(cached_results)


class CustomerAddressViewSet(viewsets.ModelViewSet):
    """Customer address management"""
    serializer_class = CustomerAddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['address_type', 'is_default']
    ordering_fields = ['created_at', 'is_default']
    ordering = ['-is_default', '-created_at']
    
    def get_queryset(self):
        return CustomerAddress.objects.filter(customer=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class OrderViewSet(viewsets.ModelViewSet):
    """Order management"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_status', 'payment_method']
    ordering_fields = ['created_at', 'total_cents']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    
    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).select_related('address')
    
    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an order"""
        order = self.get_object()
        if not order.can_be_cancelled():
            return Response(
                {'error': 'Order cannot be cancelled'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason', '')
        order.cancel_order(reason)
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)


class CartView(APIView):
    """Session-based cart management"""
    permission_classes = [permissions.AllowAny]
    
    def get_cart_key(self, request):
        """Get cart key for session or user"""
        if request.user.is_authenticated:
            return f"cart_user_{request.user.id}"
        return f"cart_session_{request.session.session_key}"
    
    def get_cart(self, request):
        """Get cart from cache or session"""
        cart_key = self.get_cart_key(request)
        cart = cache.get(cart_key, {})
        
        # If no cart in cache, try to get from session
        if not cart and not request.user.is_authenticated:
            cart = request.session.get('cart', {})
        
        return cart
    
    def save_cart(self, request, cart):
        """Save cart to cache and session"""
        cart_key = self.get_cart_key(request)
        cache.set(cart_key, cart, 86400)  # 24 hours
        
        if not request.user.is_authenticated:
            request.session['cart'] = cart
            request.session.modified = True
    
    def get(self, request):
        """Get cart contents"""
        cart = self.get_cart(request)
        
        # Convert cart to detailed format
        items = []
        total_cents = 0
        
        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(id=product_id, is_active=True)
                item_total = product.price_cents * quantity
                total_cents += item_total
                
                items.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'product_slug': product.slug,
                    'product_image': product.image.url if product.image else None,
                    'price_cents': product.price_cents,
                    'quantity': quantity,
                    'total_cents': item_total,
                })
            except Product.DoesNotExist:
                # Remove invalid products from cart
                del cart[product_id]
                self.save_cart(request, cart)
        
        serializer = CartSerializer({
            'items': items,
            'total_items': sum(cart.values()),
            'total_cents': total_cents,
            'total_display': f"KES {total_cents / 100:,.2f}"
        })
        
        return Response(serializer.data)
    
    def post(self, request):
        """Add item to cart"""
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']
            quantity = serializer.validated_data['quantity']
            
            cart = self.get_cart(request)
            current_quantity = cart.get(str(product_id), 0)
            new_quantity = current_quantity + quantity
            
            # Check stock availability
            try:
                product = Product.objects.get(id=product_id, is_active=True)
                if product.track_inventory and product.stock_quantity < new_quantity:
                    return Response(
                        {'error': f'Insufficient stock. Available: {product.stock_quantity}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                cart[str(product_id)] = new_quantity
                self.save_cart(request, cart)
                
                return Response({'message': 'Item added to cart'}, status=status.HTTP_201_CREATED)
            except Product.DoesNotExist:
                return Response(
                    {'error': 'Product not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        """Update cart item quantity"""
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')
        
        if not product_id or quantity is None:
            return Response(
                {'error': 'product_id and quantity are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if quantity <= 0:
            return Response(
                {'error': 'Quantity must be greater than 0'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            if product.track_inventory and product.stock_quantity < quantity:
                return Response(
                    {'error': f'Insufficient stock. Available: {product.stock_quantity}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            cart = self.get_cart(request)
            cart[str(product_id)] = quantity
            self.save_cart(request, cart)
            
            return Response({'message': 'Cart updated'})
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def delete(self, request):
        """Remove item from cart or clear cart"""
        product_id = request.data.get('product_id')
        
        cart = self.get_cart(request)
        
        if product_id:
            # Remove specific item
            if str(product_id) in cart:
                del cart[str(product_id)]
                self.save_cart(request, cart)
                return Response({'message': 'Item removed from cart'})
            else:
                return Response(
                    {'error': 'Item not found in cart'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Clear entire cart
            cart.clear()
            self.save_cart(request, cart)
            return Response({'message': 'Cart cleared'})


class CartToOrderView(APIView):
    """Convert cart to order"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Create order from cart"""
        cart_view = CartView()
        cart = cart_view.get_cart(request)
        
        if not cart:
            return Response(
                {'error': 'Cart is empty'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prepare order data
        order_data = {
            'address': request.data.get('address'),
            'payment_method': request.data.get('payment_method', 'cod'),
            'notes': request.data.get('notes', ''),
            'items': []
        }
        
        # Convert cart items to order items
        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(id=product_id, is_active=True)
                order_data['items'].append({
                    'product': product.id,
                    'quantity': quantity
                })
            except Product.DoesNotExist:
                return Response(
                    {'error': f'Product {product_id} not found'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Create order
        serializer = OrderCreateSerializer(data=order_data, context={'request': request})
        if serializer.is_valid():
            order = serializer.save()
            
            # Clear cart after successful order creation
            cart_view.save_cart(request, {})
            
            return Response(
                OrderSerializer(order).data, 
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminOrderViewSet(viewsets.ModelViewSet):
    """Admin order management"""
    queryset = Order.objects.all().select_related('customer', 'address')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_status', 'payment_method', 'customer']
    search_fields = ['order_number', 'customer__username', 'customer__email', 'address__full_name']
    ordering_fields = ['created_at', 'total_cents', 'status']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update order status"""
        order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Order.ORDER_STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = new_status
        
        # Update timestamps based on status
        from django.utils import timezone
        if new_status == 'confirmed' and not order.confirmed_at:
            order.confirmed_at = timezone.now()
        elif new_status == 'shipped' and not order.shipped_at:
            order.shipped_at = timezone.now()
        elif new_status == 'delivered' and not order.delivered_at:
            order.delivered_at = timezone.now()
        
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)