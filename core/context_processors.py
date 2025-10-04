def cart_context(request):
    """Add cart information to template context"""
    cart = request.session.get('cart', {})
    cart_count = sum(cart.values()) if cart else 0
    cart_items = len(cart) if cart else 0
    
    return {
        'cart_count': cart_count,
        'cart_items': cart_items,
    }
