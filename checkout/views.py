from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from cart.views import _get_cart, CART_KEY
from catalog.models import Product
from .forms import AddressForm
from .models import Address, Order, OrderItem
import random
import string

def generate_order_number():
    """Generate a unique order number in format TAC-ORD{random_string}"""
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"TAC-ORD{random_part}"

def address_view(request):
    form = AddressForm(request.POST or None)
    
    # Get cart data for the template
    cart = _get_cart(request.session)
    cart_items = []
    cart_total = 0
    cart_count = sum(cart.values()) if cart else 0
    
    for slug, qty in cart.items():
        try:
            p = Product.objects.get(slug=slug)
            subtotal = p.price_cents * qty
            cart_total += subtotal
            cart_items.append({"product": p, "qty": qty, "subtotal": subtotal/100})
        except Product.DoesNotExist:
            continue
    
    if request.method == "POST" and form.is_valid():
        request.session["address_data"] = form.cleaned_data
        return redirect("checkout:confirm")
    
    return render(request, "checkout/address.html", {
        "form": form,
        "cart_items": cart_items,
        "cart_total": cart_total/100,
        "cart_count": cart_count,
    })

def confirm_view(request):
    cart = _get_cart(request.session)
    if not cart:
        messages.error(request, "Cart is empty.")
        return redirect("cart:view")
    addr = request.session.get("address_data")
    if not addr:
        messages.error(request, "Provide address first.")
        return redirect("checkout:address")

    total = 0
    lines = []
    for slug, qty in cart.items():
        p = Product.objects.get(slug=slug)
        subtotal = p.price_cents * qty
        total += subtotal
        lines.append({"p": p, "qty": qty, "subtotal": subtotal/100})

    if request.method == "POST":
        address = Address.objects.create(**addr)
        order = Order.objects.create(
            address=address, 
            total_cents=total,
            subtotal_cents=total,
            status="processing",
            payment_status="paid",
            payment_method="cod"
        )
        
        # Create order items
        for slug, qty in cart.items():
            product = Product.objects.get(slug=slug)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                price_cents=product.price_cents,
                total_cents=product.price_cents * qty
            )
        
        request.session[CART_KEY] = {}
        request.session.pop("address_data", None)
        request.session["last_order_id"] = order.id
        messages.success(request, f"Order {order.order_number} placed successfully!")
        return redirect("checkout:done")

    return render(request, "checkout/confirm.html",
                  {"address": addr, "lines": lines, "total": total/100})

def done_view(request):
    order_id = request.session.get("last_order_id")
    if not order_id:
        messages.error(request, "No order found.")
        return redirect("catalog:product_list")
    
    order = get_object_or_404(Order, id=order_id)
    
    # Clear the session order ID and messages after displaying
    request.session.pop("last_order_id", None)
    
    # Clear all messages to remove the success message
    list(messages.get_messages(request))
    
    return render(request, "checkout/done.html", {"order": order})