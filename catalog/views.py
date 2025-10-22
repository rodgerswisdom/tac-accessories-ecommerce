from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Max
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import os
from .models import Product, Category, Tag, ProductImage
from .forms import ProductForm


DIVISION_OPTIONS = [
    {"key": "earrings", "label": "Earrings", "category_slug": "earrings"},
    {"key": "necklaces", "label": "Necklaces & Chains", "category_slug": "necklaces"},
    {"key": "bracelets", "label": "Bracelets & Bangles", "category_slug": "bracelets"},
    {"key": "rings", "label": "Rings", "category_slug": "rings"},
    {"key": "hair", "label": "Hair Accessories", "category_slug": None},
]

SORT_OPTIONS = [
    {"key": "newest", "label": "Newest"},
    {"key": "price_low", "label": "Price · Low to High"},
    {"key": "price_high", "label": "Price · High to Low"},
    {"key": "name", "label": "Name A–Z"},
    {"key": "featured", "label": "Featured"},
    {"key": "popular", "label": "Bestsellers"},
]

SORT_ORDER_MAP = {
    "newest": "-created_at",
    "price_low": "price_cents",
    "price_high": "-price_cents",
    "name": "name",
    "featured": "-is_featured",
    "popular": "-is_bestseller",
}

AVAILABILITY_OPTIONS = [
    {"key": "in_stock", "label": "Ready to ship"},
    {"key": "made_to_order", "label": "Made to order"},
]


def _apply_product_filters(request, queryset, division_map):
    state = {}

    query = request.GET.get("q", "").strip()
    if query:
        queryset = queryset.filter(
            Q(name__icontains=query)
            | Q(short_description__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
        )
        state["q"] = query

    division = request.GET.get("division")
    if division:
        state["division"] = division
        category_slug = division_map.get(division)
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        else:
            queryset = queryset.none()

    material = request.GET.get("material")
    if material:
        valid_materials = {choice[0] for choice in Product.MATERIAL_CHOICES}
        if material in valid_materials:
            queryset = queryset.filter(material=material)
            state["material"] = material

    tag_slug = request.GET.get("tag")
    if tag_slug:
        queryset = queryset.filter(tags__slug=tag_slug)
        state["tag"] = tag_slug

    availability = request.GET.get("availability")
    if availability:
        state["availability"] = availability
        if availability == "in_stock":
            queryset = queryset.filter(stock_quantity__gt=0)
        elif availability == "made_to_order":
            queryset = queryset.filter(Q(track_inventory=False) | Q(stock_quantity__lte=0))

    price_min = request.GET.get("price_min")
    if price_min:
        try:
            state["price_min"] = int(price_min)
            queryset = queryset.filter(price_cents__gte=int(price_min) * 100)
        except ValueError:
            pass

    price_max = request.GET.get("price_max")
    if price_max:
        try:
            state["price_max"] = int(price_max)
            queryset = queryset.filter(price_cents__lte=int(price_max) * 100)
        except ValueError:
            pass

    sort_key = request.GET.get("sort", "newest")
    state["sort"] = sort_key if sort_key in SORT_ORDER_MAP else "newest"
    queryset = queryset.order_by(SORT_ORDER_MAP[state["sort"]])

    return queryset, state


def product_list(request, slug=None):
    division_map = {cfg["key"]: cfg["category_slug"] for cfg in DIVISION_OPTIONS}
    categories = Category.objects.filter(is_active=True, parent__isnull=True).order_by("sort_order", "name")
    active_category = None

    products = (
        Product.objects.filter(is_active=True)
        .select_related("category")
        .prefetch_related("tags")
    )

    if slug:
        active_category = get_object_or_404(Category, slug=slug)
        products = products.filter(category=active_category)

    products, filter_state = _apply_product_filters(request, products, division_map)

    division_options = [
        {
            **option,
            "available": option["category_slug"]
            and categories.filter(slug=option["category_slug"]).exists(),
        }
        for option in DIVISION_OPTIONS
    ]

    division_notice = None
    division_key = filter_state.get("division")
    if division_key:
        for option in division_options:
            if option["key"] == division_key and not option["available"]:
                division_notice = "We are curating this collection. Book a bespoke consultation to create your set ahead of launch."
                break

    active_filters = {k: v for k, v in filter_state.items() if k not in {"sort"}}

    context = {
        "products": products,
        "active_category": active_category,
        "categories": categories,
        "division_options": division_options,
        "material_options": Product.MATERIAL_CHOICES,
        "tag_options": Tag.objects.filter(is_active=True).order_by("name"),
        "availability_options": AVAILABILITY_OPTIONS,
        "sort_options": SORT_OPTIONS,
        "filter_state": filter_state,
        "total_count": products.count(),
        "division_notice": division_notice,
        "active_filters": active_filters,
    }

    if request.headers.get("HX-Request"):
        return render(request, "catalog/_product_grid.html", context)
    return render(request, "catalog/product_list.html", context)

def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category").prefetch_related("tags", "gallery_images"),
        slug=slug,
    )
    related_products = (
        Product.objects.filter(is_active=True, category=product.category)
        .exclude(pk=product.pk)
        .select_related("category")
        [:4]
    )
    return render(
        request,
        "catalog/product_detail.html",
        {
            "product": product,
            "related_products": related_products,
        },
    )

def product_search(request):
    division_map = {cfg["key"]: cfg["category_slug"] for cfg in DIVISION_OPTIONS}
    products = (
        Product.objects.filter(is_active=True)
        .select_related("category")
        .prefetch_related("tags")
    )
    products, filter_state = _apply_product_filters(request, products, division_map)
    context = {
        "products": products,
        "filter_state": filter_state,
    }
    return render(request, "catalog/_product_grid.html", context)

def product_create(request):
    """Create a new product with step-by-step validation"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Create the product
                product = form.save(commit=False)
                product.save()
                form.save_m2m()  # Save many-to-many relationships (tags)
                
                # Handle main image
                if 'image' in request.FILES:
                    product.image = request.FILES['image']
                    product.save()
                
                # Handle gallery images
                gallery_files = request.FILES.getlist('gallery_images')
                for index, image_file in enumerate(gallery_files):
                    ProductImage.objects.create(
                        product=product,
                        image=image_file,
                        sort_order=index,
                        alt_text=f"{product.name} - Image {index + 1}"
                    )
                
                messages.success(request, f'Product "{product.name}" created successfully!')
                return redirect('catalog:product_detail', slug=product.slug)
                
            except Exception as e:
                messages.error(request, f'Error creating product: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm()
    
    return render(request, 'catalog/product_create.html', {
        'form': form,
        'categories': Category.objects.filter(is_active=True),
        'tags': Tag.objects.filter(is_active=True)
    })

@csrf_exempt
@require_http_methods(["POST"])
def upload_image(request):
    """Handle drag-and-drop image uploads"""
    try:
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'No image file provided'}, status=400)
        
        image = request.FILES['image']
        
        # Validate file type
        if not image.content_type.startswith('image/'):
            return JsonResponse({'error': 'File must be an image'}, status=400)
        
        # Validate file size (max 10MB)
        if image.size > 10 * 1024 * 1024:
            return JsonResponse({'error': 'File size must be less than 10MB'}, status=400)
        
        # Save the image
        path = default_storage.save(f'products/temp/{image.name}', ContentFile(image.read()))
        url = default_storage.url(path)
        
        return JsonResponse({
            'success': True,
            'url': url,
            'filename': image.name,
            'size': image.size
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def product_edit(request, slug):
    """Edit an existing product"""
    product = get_object_or_404(Product, slug=slug)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            try:
                product = form.save(commit=False)
                product.save()
                form.save_m2m()
                
                # Handle main image
                if 'image' in request.FILES:
                    product.image = request.FILES['image']
                    product.save()
                
                # Handle new gallery images
                gallery_files = request.FILES.getlist('gallery_images')
                if gallery_files:
                    # Get current max sort order
                    max_sort_order = product.gallery_images.aggregate(
                        max_order=Max('sort_order')
                    )['max_order'] or 0
                    
                    for index, image_file in enumerate(gallery_files):
                        ProductImage.objects.create(
                            product=product,
                            image=image_file,
                            sort_order=max_sort_order + index + 1,
                            alt_text=f"{product.name} - Image {max_sort_order + index + 1}"
                        )
                
                messages.success(request, f'Product "{product.name}" updated successfully!')
                return redirect('catalog:product_detail', slug=product.slug)
                
            except Exception as e:
                messages.error(request, f'Error updating product: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'catalog/product_edit.html', {
        'form': form,
        'product': product,
        'categories': Category.objects.filter(is_active=True),
        'tags': Tag.objects.filter(is_active=True)
    })
