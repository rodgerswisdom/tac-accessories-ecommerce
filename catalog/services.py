"""
Services for catalog operations including price resolution
"""
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from django.core.cache import cache
from django.contrib.auth.models import User
from .models import Product, ProductPrice, CurrencyRate


class PriceResolver:
    """Service for resolving product prices based on user preferences and timezone"""
    
    # Timezone to country mapping (simplified)
    TIMEZONE_TO_COUNTRY = {
        'America/New_York': 'US',
        'America/Chicago': 'US', 
        'America/Denver': 'US',
        'America/Los_Angeles': 'US',
        'Europe/London': 'GB',
        'Europe/Paris': 'FR',
        'Europe/Berlin': 'DE',
        'Europe/Rome': 'IT',
        'Europe/Madrid': 'ES',
        'Africa/Nairobi': 'KE',
        'Africa/Lagos': 'NG',
        'Africa/Johannesburg': 'ZA',
        'Africa/Accra': 'GH',
        'Africa/Cairo': 'EG',
        'Africa/Casablanca': 'MA',
        'Africa/Tunis': 'TN',
    }
    
    # Country to default currency mapping
    COUNTRY_TO_CURRENCY = {
        'US': 'USD',
        'GB': 'GBP',
        'FR': 'EUR',
        'DE': 'EUR',
        'IT': 'EUR',
        'ES': 'EUR',
        'KE': 'KES',
        'NG': 'NGN',
        'ZA': 'ZAR',
        'GH': 'GHS',
        'EG': 'EGP',
        'MA': 'MAD',
        'TN': 'TND',
    }
    
    @classmethod
    def get_country_from_timezone(cls, timezone: str) -> str:
        """Get country code from timezone"""
        return cls.TIMEZONE_TO_COUNTRY.get(timezone, 'KE')  # Default to Kenya
    
    @classmethod
    def get_currency_from_country(cls, country_code: str) -> str:
        """Get default currency for country"""
        return cls.COUNTRY_TO_CURRENCY.get(country_code, 'KES')  # Default to KES
    
    @classmethod
    def resolve_currency(cls, user: Optional[User], timezone: Optional[str] = None) -> str:
        """
        Resolve currency based on user preference or timezone
        Priority: User preference > Timezone-based country currency
        """
        # Check user preference first
        if user and hasattr(user, 'profile') and user.profile.preferred_currency:
            return user.profile.preferred_currency
        
        # Fall back to timezone-based currency
        if timezone:
            country = cls.get_country_from_timezone(timezone)
            return cls.get_currency_from_country(country)
        
        # Default fallback
        return 'KES'
    
    @classmethod
    def get_product_price(cls, product: Product, currency: str, country_code: Optional[str] = None) -> Dict:
        """
        Get resolved price for a product in specified currency
        Returns dict with price_cents, currency, display_price, and source
        """
        cache_key = f"price_{product.id}_{currency}_{country_code or 'default'}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Try to find regional price first
        regional_price = None
        if country_code:
            regional_price = ProductPrice.objects.filter(
                product=product,
                country_code=country_code,
                currency=currency,
                is_active=True
            ).first()
        
        # If no regional price, try any price in the target currency
        if not regional_price:
            regional_price = ProductPrice.objects.filter(
                product=product,
                currency=currency,
                is_active=True
            ).first()
        
        if regional_price:
            # Use regional price
            result = {
                'price_cents': regional_price.price_cents,
                'currency': regional_price.currency,
                'display_price': regional_price.price_display,
                'source': 'regional',
                'is_override': regional_price.is_override
            }
        else:
            # Convert base price using exchange rate
            base_currency = 'KES'  # Assuming base currency is KES
            if currency == base_currency:
                # Same currency, no conversion needed
                result = {
                    'price_cents': product.price_cents,
                    'currency': currency,
                    'display_price': f"{currency} {product.price_cents / 100:,.2f}",
                    'source': 'base',
                    'is_override': False
                }
            else:
                # Convert using exchange rate
                rate = CurrencyRate.get_rate(base_currency, currency)
                converted_cents = int(product.price_cents * rate)
                result = {
                    'price_cents': converted_cents,
                    'currency': currency,
                    'display_price': f"{currency} {converted_cents / 100:,.2f}",
                    'source': 'converted',
                    'is_override': False
                }
        
        # Cache for 1 hour
        cache.set(cache_key, result, 3600)
        return result
    
    @classmethod
    def get_multiple_prices(cls, product_ids: List[int], currency: str, country_code: Optional[str] = None) -> Dict[int, Dict]:
        """
        Get prices for multiple products efficiently
        """
        results = {}
        
        # Get all products
        products = Product.objects.filter(id__in=product_ids)
        product_dict = {p.id: p for p in products}
        
        # Get all regional prices for these products
        regional_prices = ProductPrice.objects.filter(
            product_id__in=product_ids,
            is_active=True
        )
        
        # Group by product and currency
        price_lookup = {}
        for price in regional_prices:
            key = (price.product_id, price.currency)
            if key not in price_lookup:
                price_lookup[key] = []
            price_lookup[key].append(price)
        
        # Resolve prices for each product
        for product_id in product_ids:
            if product_id in product_dict:
                product = product_dict[product_id]
                results[product_id] = cls.get_product_price(product, currency, country_code)
        
        return results
    
    @classmethod
    def resolve_prices_for_user(cls, user: Optional[User], timezone: Optional[str], product_ids: List[int]) -> Dict[int, Dict]:
        """
        Resolve prices for multiple products based on user context
        """
        currency = cls.resolve_currency(user, timezone)
        country_code = None
        
        if timezone:
            country_code = cls.get_country_from_timezone(timezone)
        
        return cls.get_multiple_prices(product_ids, currency, country_code)
