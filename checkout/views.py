from django.shortcuts import render, redirect
from django.contrib import messages
from cart.views import _get_cart, CART_KEY
from catalog.models import Product
from .forms import AddressForm
from .models import Address, Order

def address_view(request):
    form = AddressForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        request.session["address_data"] = form.cleaned_data
        return redirect("checkout:confirm")
    return render(request, "checkout/address.html", {"form": form})

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
        order = Order.objects.create(address=address, total_cents=total, status="paid")  # COD stub
        request.session[CART_KEY] = {}
        request.session.pop("address_data", None)
        messages.success(request, f"Order #{order.id} placed.")
        return redirect("checkout:done")

    return render(request, "checkout/confirm.html",
                  {"address": addr, "lines": lines, "total": total/100})

def done_view(request):
    return render(request, "checkout/done.html")