from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    APIException, PermissionDenied, NotAuthenticated,
    NotFound, ValidationError, Throttled
)
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger('apps.common')


class ECommerceBaseException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'A server error occurred.'
    default_code = 'error'

    def __init__(self, detail=None, code=None):
        super().__init__(detail, code)


class PaymentError(ECommerceBaseException):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = 'Payment processing failed.'
    default_code = 'payment_error'


class InsufficientStockError(ECommerceBaseException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Insufficient stock for this item.'
    default_code = 'insufficient_stock'


class OrderError(ECommerceBaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Order processing failed.'
    default_code = 'order_error'


class CartError(ECommerceBaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Cart operation failed.'
    default_code = 'cart_error'


class CouponError(ECommerceBaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid coupon.'
    default_code = 'coupon_error'


class InventoryError(ECommerceBaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Inventory operation failed.'
    default_code = 'inventory_error'


class ShippingError(ECommerceBaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Shipping calculation failed.'
    default_code = 'shipping_error'


class RefundError(ECommerceBaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Refund processing failed.'
    default_code = 'refund_error'


class ExportError(ECommerceBaseException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Export failed.'
    default_code = 'export_error'


class RateLimitExceeded(ECommerceBaseException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Rate limit exceeded. Please try again later.'
    default_code = 'rate_limit_exceeded'


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            'success': False,
            'error': {
                'status_code': response.status_code,
                'message': response.data.get('detail', str(response.data)) if isinstance(response.data, dict) else str(response.data),
                'errors': response.data if isinstance(response.data, dict) else {'detail': response.data},
            }
        }
        response.data = error_data
    else:
        logger.exception(f"Unhandled exception: {exc}", exc_info=exc)
        response = Response({
            'success': False,
            'error': {
                'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': 'An unexpected error occurred. Please try again later.',
                'errors': {},
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response
