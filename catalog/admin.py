from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Tag

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "color_display", "is_active", "product_count")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_active",)
    ordering = ("name",)

    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px;">{}</span>',
            obj.color, obj.color
        )
    color_display.short_description = "Color"

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = "Products"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "gender", "parent", "is_active", "sort_order", "product_count")
    list_filter = ("is_active", "gender", "parent")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_active", "sort_order", "gender")
    ordering = ("sort_order", "name")

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = "Products"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "material", "price_display", "stock_status", "is_featured", "is_new", "is_bestseller", "is_active", "created_at")
    list_filter = ("category", "material", "tags", "is_featured", "is_new", "is_bestseller", "is_active", "track_inventory", "created_at")
    search_fields = ("name", "sku", "description", "category__name", "material", "stone_type")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_featured", "is_new", "is_bestseller", "is_active")
    ordering = ("-created_at",)
    filter_horizontal = ("tags",)
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "slug", "sku", "category", "tags", "description", "short_description")
        }),
        ("Jewellery Details", {
            "fields": ("material", "carat", "stone_type", "stone_count", "size")
        }),
        ("Pricing", {
            "fields": ("price_cents", "compare_price_cents")
        }),
        ("Inventory", {
            "fields": ("stock_quantity", "low_stock_threshold", "track_inventory")
        }),
        ("Media", {
            "fields": ("image", "thumbnail", "gallery_images")
        }),
        ("Physical Properties", {
            "fields": ("weight_grams",)
        }),
        ("Status", {
            "fields": ("is_featured", "is_new", "is_bestseller", "is_active")
        }),
    )

    def price_display(self, obj):
        return obj.price_display
    price_display.short_description = "Price"

    def stock_status(self, obj):
        if not obj.track_inventory:
            return format_html('<span style="color: green;">Unlimited</span>')
        elif obj.stock_quantity == 0:
            return format_html('<span style="color: red;">Out of Stock</span>')
        elif obj.is_low_stock:
            return format_html('<span style="color: orange;">Low Stock ({})</span>', obj.stock_quantity)
        else:
            return format_html('<span style="color: green;">In Stock ({})</span>', obj.stock_quantity)
    stock_status.short_description = "Stock Status"