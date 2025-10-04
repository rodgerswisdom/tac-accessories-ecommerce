import django_filters
from django.db.models import Q
from catalog.models import Product, Category
from checkout.models import Order


class ProductFilter(django_filters.FilterSet):
    """Product filtering"""
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.filter(is_active=True))
    category_slug = django_filters.CharFilter(field_name='category__slug')
    min_price = django_filters.NumberFilter(field_name='price_cents', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price_cents', lookup_expr='lte')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')
    is_featured = django_filters.BooleanFilter(field_name='is_featured')
    has_discount = django_filters.BooleanFilter(method='filter_has_discount')
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Product
        fields = ['category', 'category_slug', 'min_price', 'max_price', 
                 'in_stock', 'is_featured', 'has_discount', 'search']
    
    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(track_inventory=False) | Q(stock_quantity__gt=0)
            )
        else:
            return queryset.filter(
                track_inventory=True,
                stock_quantity=0
            )
    
    def filter_has_discount(self, queryset, name, value):
        if value:
            return queryset.filter(
                compare_price_cents__isnull=False,
                compare_price_cents__gt=F('price_cents')
            )
        else:
            return queryset.filter(
                Q(compare_price_cents__isnull=True) | 
                Q(compare_price_cents__lte=F('price_cents'))
            )
    
    def filter_search(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(name__icontains=value) |
                Q(description__icontains=value) |
                Q(short_description__icontains=value) |
                Q(sku__icontains=value) |
                Q(category__name__icontains=value)
            )
        return queryset


class CategoryFilter(django_filters.FilterSet):
    """Category filtering"""
    parent = django_filters.ModelChoiceFilter(queryset=Category.objects.filter(is_active=True))
    has_products = django_filters.BooleanFilter(method='filter_has_products')
    
    class Meta:
        model = Category
        fields = ['parent', 'has_products']
    
    def filter_has_products(self, queryset, name, value):
        if value:
            return queryset.filter(products__is_active=True).distinct()
        else:
            return queryset.exclude(products__is_active=True).distinct()


class OrderFilter(django_filters.FilterSet):
    """Order filtering"""
    status = django_filters.ChoiceFilter(choices=Order.ORDER_STATUS_CHOICES)
    payment_status = django_filters.ChoiceFilter(choices=Order.PAYMENT_STATUS_CHOICES)
    payment_method = django_filters.ChoiceFilter(choices=Order.PAYMENT_METHOD_CHOICES)
    min_total = django_filters.NumberFilter(field_name='total_cents', lookup_expr='gte')
    max_total = django_filters.NumberFilter(field_name='total_cents', lookup_expr='lte')
    date_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    date_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Order
        fields = ['status', 'payment_status', 'payment_method', 
                 'min_total', 'max_total', 'date_from', 'date_to']
