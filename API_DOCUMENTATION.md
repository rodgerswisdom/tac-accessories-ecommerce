# TAC Accessories E-commerce API Documentation

## Overview

The TAC Accessories E-commerce API is a comprehensive REST API built with Django REST Framework that provides full e-commerce functionality including product management, user authentication, cart operations, and order processing.

## Base URL

```
http://localhost:8000/api/v1/
```

## Authentication

The API uses JWT (JSON Web Token) authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <your_access_token>
```

### Authentication Endpoints

#### Register User
```http
POST /api/v1/auth/register/
```

**Request Body:**
```json
{
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "securepassword123",
    "password_confirm": "securepassword123"
}
```

**Response:**
```json
{
    "user": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe"
    },
    "tokens": {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

#### Login User
```http
POST /api/v1/auth/login/
```

**Request Body:**
```json
{
    "username": "johndoe",
    "password": "securepassword123"
}
```

#### Refresh Token
```http
POST /api/v1/auth/refresh/
```

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## Products

### List Products
```http
GET /api/v1/products/
```

**Query Parameters:**
- `category` - Filter by category ID
- `category_slug` - Filter by category slug
- `min_price` - Minimum price in KES
- `max_price` - Maximum price in KES
- `in_stock` - Filter by stock availability (true/false)
- `is_featured` - Filter featured products (true/false)
- `has_discount` - Filter products with discounts (true/false)
- `search` - Search in name, description, SKU
- `ordering` - Sort by field (name, price_cents, created_at, etc.)

**Example:**
```http
GET /api/v1/products/?category=1&min_price=100&max_price=500&in_stock=true&ordering=-created_at
```

### Get Product Detail
```http
GET /api/v1/products/{id}/
```

### Search Products
```http
GET /api/v1/products/search/?q=search_term
```

### Get Featured Products
```http
GET /api/v1/products/featured/
```

## Categories

### List Categories
```http
GET /api/v1/categories/
```

**Query Parameters:**
- `parent` - Filter by parent category
- `has_products` - Filter categories with products (true/false)
- `search` - Search in name and description
- `ordering` - Sort by field

### Get Category Detail
```http
GET /api/v1/categories/{id}/
```

## Cart Management

### Get Cart
```http
GET /api/v1/cart/
```

**Response:**
```json
{
    "items": [
        {
            "product_id": 1,
            "product_name": "Test Product",
            "product_slug": "test-product",
            "product_image": "http://localhost:8000/media/products/image.jpg",
            "price_cents": 10000,
            "quantity": 2,
            "total_cents": 20000
        }
    ],
    "total_items": 2,
    "total_cents": 20000,
    "total_display": "KES 200.00"
}
```

### Add to Cart
```http
POST /api/v1/cart/
```

**Request Body:**
```json
{
    "product_id": 1,
    "quantity": 2
}
```

### Update Cart Item
```http
PUT /api/v1/cart/
```

**Request Body:**
```json
{
    "product_id": 1,
    "quantity": 3
}
```

### Remove from Cart
```http
DELETE /api/v1/cart/
```

**Request Body:**
```json
{
    "product_id": 1
}
```

### Clear Cart
```http
DELETE /api/v1/cart/
```

**Request Body:**
```json
{}
```

## Orders

### Create Order
```http
POST /api/v1/orders/
```

**Request Body:**
```json
{
    "address": {
        "full_name": "John Doe",
        "phone": "+254712345678",
        "line1": "123 Main Street",
        "line2": "Apt 4B",
        "city": "Nairobi",
        "county": "Nairobi",
        "postal_code": "00100",
        "country": "Kenya",
        "notes": "Leave at gate"
    },
    "payment_method": "cod",
    "notes": "Please deliver in the morning",
    "items": [
        {
            "product": 1,
            "quantity": 2
        }
    ]
}
```

### List Orders
```http
GET /api/v1/orders/
```

**Query Parameters:**
- `status` - Filter by order status
- `payment_status` - Filter by payment status
- `payment_method` - Filter by payment method
- `ordering` - Sort by field

### Get Order Detail
```http
GET /api/v1/orders/{id}/
```

### Cancel Order
```http
POST /api/v1/orders/{id}/cancel/
```

**Request Body:**
```json
{
    "reason": "Changed mind"
}
```

### Convert Cart to Order
```http
POST /api/v1/cart/to-order/
```

**Request Body:**
```json
{
    "address": {
        "full_name": "John Doe",
        "phone": "+254712345678",
        "line1": "123 Main Street",
        "city": "Nairobi",
        "county": "Nairobi",
        "country": "Kenya"
    },
    "payment_method": "cod",
    "notes": "Please deliver in the morning"
}
```

## User Profile

### Get Profile
```http
GET /api/v1/profile/
```

### Update Profile
```http
PUT /api/v1/profile/
```

**Request Body:**
```json
{
    "phone": "+254712345678",
    "date_of_birth": "1990-01-01",
    "gender": "male"
}
```

## Address Management

### List Addresses
```http
GET /api/v1/addresses/
```

### Create Address
```http
POST /api/v1/addresses/
```

**Request Body:**
```json
{
    "address_type": "shipping",
    "full_name": "John Doe",
    "phone": "+254712345678",
    "line1": "123 Main Street",
    "line2": "Apt 4B",
    "city": "Nairobi",
    "postal_code": "00100",
    "county": "Nairobi",
    "country": "Kenya",
    "is_default": true
}
```

### Update Address
```http
PUT /api/v1/addresses/{id}/
```

### Delete Address
```http
DELETE /api/v1/addresses/{id}/
```

## Admin Endpoints

### Admin Order Management
```http
GET /api/v1/admin/orders/
POST /api/v1/admin/orders/{id}/update-status/
```

**Update Order Status:**
```http
POST /api/v1/admin/orders/{id}/update-status/
```

**Request Body:**
```json
{
    "status": "shipped"
}
```

## Error Responses

All error responses follow this format:

```json
{
    "error": true,
    "status_code": 400,
    "message": "Bad Request",
    "details": {
        "field_name": ["Error message"]
    }
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Anonymous users**: 100 requests/hour
- **Authenticated users**: 1000 requests/hour
- **Login attempts**: 20 requests/hour
- **Registration**: 10 requests/hour
- **Cart operations**: 200 requests/hour
- **Order operations**: 50 requests/hour
- **Search**: 300 requests/hour
- **Admin operations**: 5000 requests/hour

## Pagination

List endpoints support pagination:

```json
{
    "count": 100,
    "next": "http://localhost:8000/api/v1/products/?page=2",
    "previous": null,
    "page_size": 20,
    "current_page": 1,
    "total_pages": 5,
    "results": [...]
}
```

## Filtering and Search

Most list endpoints support filtering and search:

- **Filtering**: Use query parameters to filter results
- **Search**: Use the `search` parameter for text search
- **Ordering**: Use the `ordering` parameter to sort results

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/

## Security Features

- JWT authentication with refresh tokens
- Rate limiting to prevent abuse
- CORS configuration for cross-origin requests
- Input validation and sanitization
- Secure session management
- Admin-only endpoints for sensitive operations

## Example Usage

### Complete Order Flow

1. **Register/Login**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "johndoe", "email": "john@example.com", "first_name": "John", "last_name": "Doe", "password": "securepass123", "password_confirm": "securepass123"}'
```

2. **Browse Products**:
```bash
curl http://localhost:8000/api/v1/products/
```

3. **Add to Cart**:
```bash
curl -X POST http://localhost:8000/api/v1/cart/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 2}'
```

4. **Create Order**:
```bash
curl -X POST http://localhost:8000/api/v1/orders/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"address": {"full_name": "John Doe", "phone": "+254712345678", "line1": "123 Main St", "city": "Nairobi", "county": "Nairobi", "country": "Kenya"}, "payment_method": "cod", "items": [{"product": 1, "quantity": 2}]}'
```

## Support

For API support and questions, please contact the development team or refer to the interactive documentation at `/api/docs/`.
