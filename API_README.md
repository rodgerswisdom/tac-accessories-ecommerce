# TAC Accessories E-commerce API

A comprehensive, secure, and scalable REST API for the TAC Accessories e-commerce platform built with Django REST Framework.

## 🚀 Features

### Core Functionality
- **Product Management**: Browse, search, and filter products with images and inventory tracking
- **User Authentication**: JWT-based authentication with registration, login, and profile management
- **Shopping Cart**: Session-based cart management with seamless user experience
- **Order Processing**: Complete order lifecycle from creation to delivery tracking
- **Address Management**: Multiple shipping and billing addresses per user
- **Admin Panel**: Comprehensive admin endpoints for inventory and order management

### Security Features
- **JWT Authentication**: Secure token-based authentication with refresh tokens
- **Rate Limiting**: Configurable rate limits to prevent abuse
- **CORS Support**: Cross-origin resource sharing for frontend integration
- **Input Validation**: Comprehensive data validation and sanitization
- **Permission System**: Role-based access control for different user types

### Scalability Features
- **Caching**: Redis-based caching for improved performance
- **Pagination**: Efficient pagination for large datasets
- **Filtering & Search**: Advanced filtering and search capabilities
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation
- **Error Handling**: Comprehensive error handling with detailed responses

## 📋 Requirements

- Python 3.12+
- Django 5.2.7
- Django REST Framework 3.15.2
- PostgreSQL (production) / SQLite (development)
- Redis (for caching and rate limiting)

## 🛠 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd tac-accessories-ecommerce
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Database setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run the server**
   ```bash
   python manage.py runserver
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Django Settings
DEBUG=true
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3
# For PostgreSQL: DATABASE_URL=postgresql://user:password@localhost:5432/tac_ecomm

# Redis (for caching and rate limiting)
REDIS_URL=redis://localhost:6379/0

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### API Configuration

The API is configured with the following settings:

- **Authentication**: JWT with 1-hour access tokens and 7-day refresh tokens
- **Rate Limiting**: Configurable per endpoint (see API documentation)
- **Pagination**: 20 items per page by default
- **CORS**: Enabled for development, configurable for production

## 📚 API Documentation

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### Base URL

```
http://localhost:8000/api/v1/
```

### Authentication

Include the JWT access token in the Authorization header:

```
Authorization: Bearer <your_access_token>
```

## 🔐 Security

### Authentication Flow

1. **Register/Login**: Get access and refresh tokens
2. **API Requests**: Include access token in Authorization header
3. **Token Refresh**: Use refresh token to get new access token
4. **Logout**: Tokens expire automatically

### Rate Limiting

| Endpoint Type | Anonymous | Authenticated | Admin |
|---------------|-----------|---------------|-------|
| General API   | 100/hour  | 1000/hour     | 5000/hour |
| Login         | 20/hour   | -             | - |
| Registration  | 10/hour   | -             | - |
| Cart          | 200/hour  | 200/hour      | - |
| Orders        | -         | 50/hour       | 5000/hour |
| Search        | 300/hour  | 300/hour      | - |

### CORS Configuration

The API supports CORS for frontend integration. Configure allowed origins in settings:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://yourdomain.com",
]
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
python manage.py test

# Run specific test modules
python manage.py test api.tests.AuthenticationAPITest
python manage.py test api.tests.ProductAPITest
```

### Test Coverage

The API includes comprehensive tests for:
- Authentication and authorization
- Product management
- Cart operations
- Order processing
- Admin functionality
- Rate limiting
- Error handling

## 📊 Monitoring and Logging

### Logging

The API logs important events:
- User registration and login
- Order creation and updates
- Product changes
- API errors and exceptions

### Monitoring

Monitor the API using:
- Django admin interface
- API documentation endpoints
- Server logs
- Database queries

## 🚀 Deployment

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure proper `SECRET_KEY`
- [ ] Set up PostgreSQL database
- [ ] Configure Redis for caching
- [ ] Set up proper `ALLOWED_HOSTS`
- [ ] Configure CORS origins
- [ ] Set up SSL/HTTPS
- [ ] Configure static file serving
- [ ] Set up logging
- [ ] Configure backup strategy

### Docker Deployment

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput
RUN python manage.py migrate

EXPOSE 8000
CMD ["gunicorn", "tac_ecomm.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Environment Variables for Production

```env
DEBUG=false
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost:5432/tac_ecomm
REDIS_URL=redis://localhost:6379/0
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## 🔌 Integration Examples

### Frontend Integration

```javascript
// React/Next.js example
const apiClient = {
  baseURL: 'http://localhost:8000/api/v1',
  
  async login(username, password) {
    const response = await fetch(`${this.baseURL}/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    return response.json();
  },
  
  async getProducts() {
    const response = await fetch(`${this.baseURL}/products/`);
    return response.json();
  }
};
```

### Mobile App Integration

```python
# Python client example
from api_client_example import TACAPIClient

client = TACAPIClient("https://api.yourdomain.com/api/v1")
client.login("username", "password")
products = client.get_products()
```

## 📈 Performance Optimization

### Caching

- **Product Search**: 5-minute cache for search results
- **Cart Data**: 24-hour cache for cart contents
- **User Sessions**: Configurable session timeout

### Database Optimization

- **Select Related**: Optimized queries with select_related
- **Pagination**: Efficient pagination for large datasets
- **Indexing**: Proper database indexes for common queries

### API Optimization

- **Compression**: Gzip compression for responses
- **Rate Limiting**: Prevents abuse and ensures fair usage
- **Connection Pooling**: Efficient database connections

## 🛠 Development

### Adding New Endpoints

1. Create serializer in `api/serializers.py`
2. Create view in `api/views.py`
3. Add URL pattern in `api/urls.py`
4. Add tests in `api/tests.py`
5. Update documentation

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write comprehensive docstrings
- Include unit tests for new features

## 📞 Support

For API support and questions:

- **Documentation**: Check the interactive docs at `/api/docs/`
- **Issues**: Report bugs and feature requests
- **Email**: Contact the development team

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Django and Django REST Framework
- JWT authentication
- OpenAPI/Swagger documentation
- All contributors and the open-source community
