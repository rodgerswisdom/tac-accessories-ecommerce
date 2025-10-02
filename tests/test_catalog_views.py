import pytest
from django.test import Client
from catalog.models import Category, Product

@pytest.mark.django_db
def test_product_list_view():
    client = Client()
    response = client.get('/shop/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_product_detail_view():
    category = Category.objects.create(name="Electronics", slug="electronics")
    product = Product.objects.create(
        category=category,
        name="Laptop",
        slug="laptop",
        price_cents=50000
    )
    client = Client()
    response = client.get(f'/shop/p/{product.slug}/')
    assert response.status_code == 200
