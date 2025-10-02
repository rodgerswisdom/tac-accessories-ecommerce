# tac_ecomm - Django 5 + HTMX E-commerce Application

A modern, full-featured e-commerce application built with Django 5, HTMX, and Tailwind CSS.

## 🚀 Features

- **Product Catalog** with categories and search functionality
- **HTMX Integration** for dynamic search without page reloads
- **Session-based Shopping Cart** with add/remove/clear operations
- **User Authentication** with signup and login
- **Checkout Flow** with address collection and order processing
- **Admin Interface** for managing products and categories
- **Responsive Design** with Tailwind CSS
- **Environment Configuration** with django-environ
- **Postgres-ready** with SQLite as default
- **Comprehensive Testing** with pytest

## 🛠 Tech Stack

- **Backend**: Django 5.2.7, Python 3.13+
- **Frontend**: HTMX 2.x, Tailwind CSS
- **Database**: SQLite (default), PostgreSQL (production-ready)
- **Static Files**: Whitenoise
- **Testing**: pytest, pytest-django
- **Code Quality**: ruff, black, mypy

## 📦 Installation

### Prerequisites
- Python 3.12+
- pip

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/tac_ecomm.git
   cd tac_ecomm
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
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

6. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

Visit `http://localhost:8000/` to see the application.

## 🧪 Testing

Run the test suite:
```bash
pytest
```

## 📁 Project Structure

```
tac_ecomm/
├── core/           # Base templates, home view, static files
├── catalog/        # Products, categories, search functionality
├── cart/           # Session-based shopping cart
├── checkout/       # Order processing, addresses
├── accounts/       # User authentication
├── tests/          # Test suite
├── staticfiles/    # Collected static files
└── tac_ecomm/      # Django project settings
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
DEBUG=true
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
CSRF_TRUSTED_ORIGINS=
```

### Database Configuration

- **Development**: SQLite (default)
- **Production**: Set `DATABASE_URL` to your PostgreSQL connection string

Example PostgreSQL URL:
```
DATABASE_URL=postgresql://user:password@localhost:5432/tac_ecomm
```

## 🎯 Usage

### Admin Interface
- Access at `/admin/`
- Create categories and products
- Manage orders and addresses

### Shopping Flow
1. Browse products at `/shop/`
2. Use HTMX search for dynamic filtering
3. Add products to cart
4. Proceed to checkout
5. Enter delivery address
6. Confirm and place order

### User Authentication
- Sign up at `/accounts/signup/`
- Login at `/accounts/login/`
- Logout at `/accounts/logout/`

## 🚀 Deployment

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Configure proper `SECRET_KEY`
- [ ] Set up PostgreSQL database
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up static file serving
- [ ] Configure CSRF trusted origins
- [ ] Set up proper logging

### Environment Variables for Production
```env
DEBUG=false
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost:5432/tac_ecomm
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django framework
- HTMX for dynamic interactions
- Tailwind CSS for styling
- All contributors and the open-source community
