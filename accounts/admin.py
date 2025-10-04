from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import CustomerProfile, CustomerAddress

class CustomerProfileInline(admin.StackedInline):
    model = CustomerProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (CustomerProfileInline,)

@admin.register(CustomerAddress)
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = ("customer", "full_name", "city", "county", "address_type", "is_default", "created_at")
    list_filter = ("address_type", "is_default", "county", "city")
    search_fields = ("customer__username", "customer__email", "full_name", "line1", "city")
    list_editable = ("is_default",)
    ordering = ("-is_default", "-created_at")

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
