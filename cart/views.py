from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from catalog.models import Product

CART_KEY = "cart"

def _get_cart(session):
    return session.setdefault(CART_KEY, {})

def cart_view(request):
    cart = _get_cart(request.session)
    items, total = [], 0
    cart_count = sum(cart.values()) if cart else 0
    cart_items = len(cart) if cart else 0
    
    for slug, qty in cart.items():
        p = get_object_or_404(Product, slug=slug)
        subtotal = p.price_cents * qty
        total += subtotal
        items.append({"product": p, "qty": qty, "subtotal": subtotal/100})
    
    return render(request, "cart/cart.html", {
        "items": items, 
        "total": total/100,
        "cart_count": cart_count,
        "cart_items": cart_items,
    })

def cart_add(request, slug):
    p = get_object_or_404(Product, slug=slug)
    cart = _get_cart(request.session)
    cart[slug] = cart.get(slug, 0) + 1
    request.session.modified = True
    return redirect("cart:view")

def cart_remove(request, slug):
    cart = _get_cart(request.session)
    if slug in cart:
        del cart[slug]
        request.session.modified = True
    return redirect("cart:view")

def cart_clear(request):
    request.session[CART_KEY] = {}
    request.session.modified = True
    return redirect("cart:view")

def cart_count(request):
    """Return cart count as JSON"""
    cart = _get_cart(request.session)
    cart_count = sum(cart.values()) if cart else 0
    cart_items = len(cart) if cart else 0
    
    return JsonResponse({
        'cart_count': cart_count,
        'cart_items': cart_items,
    })