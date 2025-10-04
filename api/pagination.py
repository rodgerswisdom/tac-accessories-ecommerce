from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for most endpoints"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductPagination(PageNumberPagination):
    """Pagination optimized for product listings"""
    page_size = 24  # Good for grid layouts
    page_size_query_param = 'page_size'
    max_page_size = 100


class OrderPagination(PageNumberPagination):
    """Pagination for order listings"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class CustomPagination(PageNumberPagination):
    """Custom pagination with additional metadata"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page_size': self.page_size,
            'current_page': self.page.number,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })
