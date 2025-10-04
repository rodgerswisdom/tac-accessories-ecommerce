#!/usr/bin/env python3
"""
TAC Accessories E-commerce API Client Example

This script demonstrates how to use the TAC Accessories E-commerce API
to perform common operations like browsing products, managing cart, and creating orders.
"""

import requests
import json
from typing import Dict, Any, Optional


class TACAPIClient:
    """Client for TAC Accessories E-commerce API"""
    
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication if available"""
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers
    
    def register(self, username: str, email: str, first_name: str, last_name: str, password: str) -> Dict[str, Any]:
        """Register a new user"""
        url = f"{self.base_url}/auth/register/"
        data = {
            "username": username,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "password": password,
            "password_confirm": password
        }
        
        response = self.session.post(url, json=data, headers=self._get_headers())
        response.raise_for_status()
        
        result = response.json()
        self.access_token = result["tokens"]["access"]
        self.refresh_token = result["tokens"]["refresh"]
        
        return result
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login user"""
        url = f"{self.base_url}/auth/login/"
        data = {
            "username": username,
            "password": password
        }
        
        response = self.session.post(url, json=data, headers=self._get_headers())
        response.raise_for_status()
        
        result = response.json()
        self.access_token = result["tokens"]["access"]
        self.refresh_token = result["tokens"]["refresh"]
        
        return result
    
    def get_products(self, **filters) -> Dict[str, Any]:
        """Get products with optional filters"""
        url = f"{self.base_url}/products/"
        params = {k: v for k, v in filters.items() if v is not None}
        
        response = self.session.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()
        
        return response.json()
    
    def get_product(self, product_id: int) -> Dict[str, Any]:
        """Get product details"""
        url = f"{self.base_url}/products/{product_id}/"
        
        response = self.session.get(url, headers=self._get_headers())
        response.raise_for_status()
        
        return response.json()
    
    def search_products(self, query: str) -> Dict[str, Any]:
        """Search products"""
        url = f"{self.base_url}/products/search/"
        params = {"q": query}
        
        response = self.session.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()
        
        return response.json()
    
    def get_cart(self) -> Dict[str, Any]:
        """Get cart contents"""
        url = f"{self.base_url}/cart/"
        
        response = self.session.get(url, headers=self._get_headers())
        response.raise_for_status()
        
        return response.json()
    
    def add_to_cart(self, product_id: int, quantity: int = 1) -> Dict[str, Any]:
        """Add item to cart"""
        url = f"{self.base_url}/cart/"
        data = {
            "product_id": product_id,
            "quantity": quantity
        }
        
        response = self.session.post(url, json=data, headers=self._get_headers())
        response.raise_for_status()
        
        return response.json()
    
    def update_cart_item(self, product_id: int, quantity: int) -> Dict[str, Any]:
        """Update cart item quantity"""
        url = f"{self.base_url}/cart/"
        data = {
            "product_id": product_id,
            "quantity": quantity
        }
        
        response = self.session.put(url, json=data, headers=self._get_headers())
        response.raise_for_status()
        
        return response.json()
    
    def remove_from_cart(self, product_id: int) -> Dict[str, Any]:
        """Remove item from cart"""
        url = f"{self.base_url}/cart/"
        data = {"product_id": product_id}
        
        response = self.session.delete(url, json=data, headers=self._get_headers())
        response.raise_for_status()
        
        return response.json()
    
    def clear_cart(self) -> Dict[str, Any]:
        """Clear entire cart"""
        url = f"{self.base_url}/cart/"
        
        response = self.session.delete(url, headers=self._get_headers())
        response.raise_for_status()
        
        return response.json()
    
    def create_order(self, address: Dict[str, str], payment_method: str = "cod", notes: str = "") -> Dict[str, Any]:
        """Create order from cart"""
        url = f"{self.base_url}/cart/to-order/"
        data = {
            "address": address,
            "payment_method": payment_method,
            "notes": notes
        }
        
        response = self.session.post(url, json=data, headers=self._get_headers())
        response.raise_for_status()
        
        return response.json()
    
    def get_orders(self) -> Dict[str, Any]:
        """Get user orders"""
        url = f"{self.base_url}/orders/"
        
        response = self.session.get(url, headers=self._get_headers())
        response.raise_for_status()
        
        return response.json()
    
    def get_order(self, order_id: int) -> Dict[str, Any]:
        """Get order details"""
        url = f"{self.base_url}/orders/{order_id}/"
        
        response = self.session.get(url, headers=self._get_headers())
        response.raise_for_status()
        
        return response.json()
    
    def cancel_order(self, order_id: int, reason: str = "") -> Dict[str, Any]:
        """Cancel order"""
        url = f"{self.base_url}/orders/{order_id}/cancel/"
        data = {"reason": reason}
        
        response = self.session.post(url, json=data, headers=self._get_headers())
        response.raise_for_status()
        
        return response.json()


def main():
    """Example usage of the API client"""
    client = TACAPIClient()
    
    try:
        # Register a new user
        print("Registering new user...")
        user_data = client.register(
            username="testuser123",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="testpass123"
        )
        print(f"User registered: {user_data['user']['username']}")
        
        # Browse products
        print("\nBrowsing products...")
        products = client.get_products()
        print(f"Found {products['count']} products")
        
        if products['results']:
            product = products['results'][0]
            print(f"First product: {product['name']} - {product['price_display']}")
            
            # Add to cart
            print(f"\nAdding {product['name']} to cart...")
            client.add_to_cart(product['id'], quantity=2)
            
            # View cart
            print("\nCart contents:")
            cart = client.get_cart()
            for item in cart['items']:
                print(f"- {item['product_name']} x {item['quantity']} = {item['total_display']}")
            print(f"Total: {cart['total_display']}")
            
            # Create order
            print("\nCreating order...")
            address = {
                "full_name": "Test User",
                "phone": "+254712345678",
                "line1": "123 Test Street",
                "city": "Nairobi",
                "county": "Nairobi",
                "country": "Kenya"
            }
            
            order = client.create_order(address, payment_method="cod", notes="Test order")
            print(f"Order created: {order['order_number']}")
            print(f"Status: {order['status']}")
            print(f"Total: {order['total_display']}")
            
            # View orders
            print("\nUser orders:")
            orders = client.get_orders()
            for order in orders['results']:
                print(f"- Order {order['order_number']}: {order['status']} - {order['total_display']}")
        
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
