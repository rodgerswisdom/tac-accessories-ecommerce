from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price_cents", "in_stock", "created_at")
    list_filter = ("category", "in_stock")
    search_fields = ("name", "slug", "category__name")
    prepopulated_fields = {"slug": ("name",)}