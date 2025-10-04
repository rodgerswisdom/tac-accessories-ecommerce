from rest_framework.throttling import UserRateThrottle, AnonRateThrottle, ScopedRateThrottle


class LoginRateThrottle(UserRateThrottle):
    """Rate limiting for login attempts"""
    scope = 'login'


class RegistrationRateThrottle(AnonRateThrottle):
    """Rate limiting for registration attempts"""
    scope = 'registration'


class CartRateThrottle(UserRateThrottle):
    """Rate limiting for cart operations"""
    scope = 'cart'


class OrderRateThrottle(UserRateThrottle):
    """Rate limiting for order operations"""
    scope = 'order'


class ProductSearchRateThrottle(AnonRateThrottle):
    """Rate limiting for product search"""
    scope = 'search'


class AdminRateThrottle(UserRateThrottle):
    """Rate limiting for admin operations"""
    scope = 'admin'
