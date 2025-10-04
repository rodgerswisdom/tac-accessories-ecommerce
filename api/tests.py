from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from catalog.models import Category, Product
from accounts.models import CustomerProfile
from checkout.models import Order, OrderItem, Address


class APITestCase(APITestCase):
    """Base test case for API tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create test category
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category',
            description='Test category description'
        )
        
        # Create test product
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            description='Test product description',
            price_cents=10000,  # KES 100.00
            category=self.category,
            stock_quantity=10
        )
        
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
    
    def authenticate_user(self, user=None):
        """Authenticate a user for API requests"""
        if user is None:
            user = self.user
        
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        return refresh.access_token
    
    def authenticate_admin(self):
        """Authenticate admin user"""
        return self.authenticate_user(self.admin_user)


class AuthenticationAPITest(APITestCase):
    """Test authentication endpoints"""
    
    def test_user_registration(self):
        """Test user registration"""
        url = reverse('api:register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('user', response.data)
    
    def test_user_login(self):
        """Test user login"""
        url = reverse('api:login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('user', response.data)
    
    def test_invalid_login(self):
        """Test invalid login credentials"""
        url = reverse('api:login')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProductAPITest(APITestCase):
    """Test product API endpoints"""
    
    def test_product_list(self):
        """Test product listing"""
        url = reverse('api:product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_product_detail(self):
        """Test product detail"""
        url = reverse('api:product-detail', kwargs={'pk': self.product.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Product')
    
    def test_product_search(self):
        """Test product search"""
        url = reverse('api:product-search')
        response = self.client.get(url, {'q': 'test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_featured_products(self):
        """Test featured products endpoint"""
        # Make product featured
        self.product.is_featured = True
        self.product.save()
        
        url = reverse('api:product-featured')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class CartAPITest(APITestCase):
    """Test cart API endpoints"""
    
    def test_add_to_cart(self):
        """Test adding item to cart"""
        url = reverse('api:cart')
        data = {
            'product_id': self.product.id,
            'quantity': 2
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_get_cart(self):
        """Test getting cart contents"""
        # Add item to cart first
        self.test_add_to_cart()
        
        url = reverse('api:cart')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 1)
    
    def test_update_cart_item(self):
        """Test updating cart item quantity"""
        # Add item to cart first
        self.test_add_to_cart()
        
        url = reverse('api:cart')
        data = {
            'product_id': self.product.id,
            'quantity': 5
        }
        
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_remove_from_cart(self):
        """Test removing item from cart"""
        # Add item to cart first
        self.test_add_to_cart()
        
        url = reverse('api:cart')
        data = {
            'product_id': self.product.id
        }
        
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class OrderAPITest(APITestCase):
    """Test order API endpoints"""
    
    def setUp(self):
        super().setUp()
        self.authenticate_user()
    
    def test_create_order(self):
        """Test creating an order"""
        url = reverse('api:order-list')
        data = {
            'address': {
                'full_name': 'Test User',
                'phone': '+254712345678',
                'line1': '123 Test Street',
                'city': 'Nairobi',
                'county': 'Nairobi',
                'country': 'Kenya'
            },
            'payment_method': 'cod',
            'notes': 'Test order',
            'items': [
                {
                    'product': self.product.id,
                    'quantity': 2
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('order_number', response.data)
    
    def test_get_orders(self):
        """Test getting user orders"""
        # Create an order first
        self.test_create_order()
        
        url = reverse('api:order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_cancel_order(self):
        """Test cancelling an order"""
        # Create an order first
        self.test_create_order()
        
        # Get the created order
        order = Order.objects.filter(customer=self.user).first()
        
        url = reverse('api:order-cancel', kwargs={'pk': order.pk})
        data = {'reason': 'Changed mind'}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'cancelled')


class AdminAPITest(APITestCase):
    """Test admin API endpoints"""
    
    def setUp(self):
        super().setUp()
        self.authenticate_admin()
    
    def test_admin_order_list(self):
        """Test admin order listing"""
        # Create an order first
        order = Order.objects.create(
            customer=self.user,
            address=Address.objects.create(
                full_name='Test User',
                phone='+254712345678',
                line1='123 Test Street',
                city='Nairobi'
            ),
            total_cents=20000
        )
        
        url = reverse('api:admin-order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_update_order_status(self):
        """Test updating order status"""
        # Create an order first
        order = Order.objects.create(
            customer=self.user,
            address=Address.objects.create(
                full_name='Test User',
                phone='+254712345678',
                line1='123 Test Street',
                city='Nairobi'
            ),
            total_cents=20000
        )
        
        url = reverse('api:admin-order-update-status', kwargs={'pk': order.pk})
        data = {'status': 'confirmed'}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'confirmed')


class RateLimitTest(APITestCase):
    """Test rate limiting"""
    
    def test_login_rate_limit(self):
        """Test login rate limiting"""
        url = reverse('api:login')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        # Make multiple failed login attempts
        for _ in range(25):  # Exceed the 20/hour limit
            response = self.client.post(url, data, format='json')
        
        # Should be rate limited
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)