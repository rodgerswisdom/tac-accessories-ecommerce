from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Category

def product_list(request, slug=None):
    qs = Product.objects.select_related("category")
    category = None
    if slug:
        category = get_object_or_404(Category, slug=slug)
        qs = qs.filter(category=category)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(category__name__icontains=q))
    
    # Handle sorting
    sort = request.GET.get("sort", "created_at")
    if sort:
        qs = qs.order_by(sort)
    
    ctx = {"products": qs, "active_category": category, "categories": Category.objects.all()}
    if request.headers.get("HX-Request"):
        return render(request, "catalog/_product_grid.html", ctx)
    return render(request, "catalog/product_list.html", ctx)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, "catalog/product_detail.html", {"product": product})

def product_search(request):
    q = request.GET.get("q", "").strip()
    qs = Product.objects.select_related("category")
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(category__name__icontains=q))
    return render(request, "catalog/_product_grid.html", {"products": qs, "categories": Category.objects.all()})