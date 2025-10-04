from django.contrib import admin
from django.utils.html import format_html
from .models import Address, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("total_cents", "price_display", "total_display")
    fields = ("product", "quantity", "price_cents", "total_cents", "price_display", "total_display")

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "city", "county", "created_at")
    list_filter = ("county", "city", "created_at")
    search_fields = ("full_name", "phone", "line1", "city")
    ordering = ("-created_at",)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "customer", "status", "payment_status", "total_display", "created_at")
    list_filter = ("status", "payment_status", "payment_method", "created_at")
    search_fields = ("order_number", "customer__username", "customer__email", "address__full_name")
    list_editable = ("status", "payment_status")
    ordering = ("-created_at",)
    inlines = [OrderItemInline]
    readonly_fields = ("order_number", "created_at", "updated_at", "subtotal_display", "shipping_display", "tax_display", "total_display")
    
    fieldsets = (
        ("Order Information", {
            "fields": ("order_number", "customer", "status", "payment_status", "payment_method")
        }),
        ("Address", {
            "fields": ("address",)
        }),
        ("Financial", {
            "fields": ("subtotal_cents", "subtotal_display", "shipping_cost_cents", "shipping_display", "tax_cents", "tax_display", "total_cents", "total_display")
        }),
        ("Notes", {
            "fields": ("notes", "internal_notes")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at", "confirmed_at", "shipped_at", "delivered_at", "cancelled_at"),
            "classes": ("collapse",)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer', 'address')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "price_display", "total_display")
    list_filter = ("order__status", "created_at")
    search_fields = ("order__order_number", "product__name", "product__sku")
    ordering = ("-created_at",)
    readonly_fields = ("total_cents", "price_display", "total_display")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'product')
