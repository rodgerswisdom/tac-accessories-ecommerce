import pytest
from catalog.models import Category, Product

@pytest.mark.django_db
def test_category_str():
    category = Category.objects.create(name="Electronics", slug="electronics")
    assert str(category) == "Electronics"

@pytest.mark.django_db
def test_product_str():
    category = Category.objects.create(name="Electronics", slug="electronics")
    product = Product.objects.create(
        category=category,
        name="Laptop",
        slug="laptop",
        price_cents=50000
    )
    assert str(product) == "Laptop"

@pytest.mark.django_db
def test_product_price_display():
    category = Category.objects.create(name="Electronics", slug="electronics")
    product = Product.objects.create(
        category=category,
        name="Laptop",
        slug="laptop",
        price_cents=50000
    )
    assert product.price_display == "KES 500.00"
