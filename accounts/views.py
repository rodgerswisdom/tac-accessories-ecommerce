from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CustomerProfile

def login_view(request):
    if request.method == "POST":
        u = request.POST.get("username"); p = request.POST.get("password")
        user = authenticate(request, username=u, password=p)
        if user:
            login(request, user); return redirect("core:home")
        messages.error(request, "Invalid credentials.")
    return render(request, "accounts/login.html")

def logout_view(request):
    logout(request)
    return redirect("core:home")

def signup_view(request):
    if request.method == "POST":
        u = request.POST.get("username"); p = request.POST.get("password")
        if not u or not p:
            messages.error(request, "Username and password required.")
        elif User.objects.filter(username=u).exists():
            messages.error(request, "Username taken.")
        else:
            User.objects.create_user(username=u, password=p)
            messages.success(request, "Account created. Please log in.")
            return redirect("accounts:login")
    return render(request, "accounts/signup.html")


@login_required
def profile_view(request):
    """User profile management view"""
    try:
        profile = request.user.profile
    except CustomerProfile.DoesNotExist:
        profile = CustomerProfile.objects.create(user=request.user)
    
    if request.method == "POST":
        # Update profile fields
        profile.phone = request.POST.get('phone', profile.phone)
        profile.date_of_birth = request.POST.get('date_of_birth') or profile.date_of_birth
        profile.gender = request.POST.get('gender', profile.gender)
        profile.preferred_currency = request.POST.get('preferred_currency', profile.preferred_currency)
        
        # Handle avatar upload
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        
        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("accounts:profile")
    
    context = {
        'profile': profile,
        'currency_choices': CustomerProfile.CURRENCY_CHOICES,
    }
    return render(request, "accounts/profile.html", context)