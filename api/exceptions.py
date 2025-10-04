from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from django.http import Http404
from django.db import IntegrityError


def custom_exception_handler(exc, context):
    """
    Custom exception handler for API responses
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'error': True,
            'status_code': response.status_code,
            'message': 'An error occurred',
            'details': response.data
        }
        
        # Handle specific error types
        if response.status_code == 400:
            custom_response_data['message'] = 'Bad Request'
        elif response.status_code == 401:
            custom_response_data['message'] = 'Authentication required'
        elif response.status_code == 403:
            custom_response_data['message'] = 'Permission denied'
        elif response.status_code == 404:
            custom_response_data['message'] = 'Resource not found'
        elif response.status_code == 405:
            custom_response_data['message'] = 'Method not allowed'
        elif response.status_code == 429:
            custom_response_data['message'] = 'Rate limit exceeded'
        elif response.status_code == 500:
            custom_response_data['message'] = 'Internal server error'
        
        response.data = custom_response_data
    
    return response


class APIException(Exception):
    """Base API exception"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A server error occurred.'
    default_code = 'error'
    
    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
        
        self.detail = detail
        self.code = code


class ValidationException(APIException):
    """Validation exception"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Validation error occurred.'
    default_code = 'validation_error'


class NotFoundException(APIException):
    """Not found exception"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Resource not found.'
    default_code = 'not_found'


class PermissionException(APIException):
    """Permission exception"""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Permission denied.'
    default_code = 'permission_denied'


class AuthenticationException(APIException):
    """Authentication exception"""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Authentication required.'
    default_code = 'authentication_required'


class RateLimitException(APIException):
    """Rate limit exception"""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Rate limit exceeded.'
    default_code = 'rate_limit_exceeded'
