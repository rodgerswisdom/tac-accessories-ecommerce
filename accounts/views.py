from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

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