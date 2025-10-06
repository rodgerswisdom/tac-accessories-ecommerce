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
