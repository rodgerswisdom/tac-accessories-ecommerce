from django.shortcuts import render
from catalog.models import Product

def home(request):
    # Get featured products (limit to 3 for homepage display)
    featured_products = Product.objects.filter(
        is_active=True, 
        is_featured=True
    ).select_related('category')[:3]
    
    context = {
        'featured_products': featured_products,
    }
    return render(request, "home.html", context)