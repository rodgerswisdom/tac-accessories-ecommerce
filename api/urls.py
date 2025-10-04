from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

# Create router for viewsets
router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'addresses', views.CustomerAddressViewSet, basename='address')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'admin/orders', views.AdminOrderViewSet, basename='admin-order')

app_name = 'api'

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.UserRegistrationView.as_view(), name='register'),
    path('auth/login/', views.UserLoginView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User profile endpoints
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    
    # Cart endpoints
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/to-order/', views.CartToOrderView.as_view(), name='cart-to-order'),
    
    # Include router URLs
    path('', include(router.urls)),
]
