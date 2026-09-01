from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.conf import settings


class HealthCheckView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        from django.db import connection
        from django.core.cache import cache
        health = {
            'status': 'healthy',
            'database': 'ok',
            'cache': 'ok',
        }
        try:
            connection.ensure_connection()
        except Exception as e:
            health['database'] = f'error: {str(e)}'
            health['status'] = 'degraded'

        try:
            cache.set('health_check', 'ok', 5)
            cache.get('health_check')
        except Exception as e:
            health['cache'] = f'error: {str(e)}'
            health['status'] = 'degraded'

        status_code = status.HTTP_200_OK if health['status'] == 'healthy' else status.HTTP_503_SERVICE_UNAVAILABLE
        return Response(health, status=status_code)


class APIMetaView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({
            'api_version': 'v1',
            'api_name': 'E-Commerce API',
            'available_endpoints': {
                'products': '/api/v1/products/',
                'categories': '/api/v1/categories/',
                'users': '/api/v1/users/',
                'orders': '/api/v1/orders/',
                'cart': '/api/v1/cart/',
                'payments': '/api/v1/payments/',
                'reviews': '/api/v1/reviews/',
                'inventory': '/api/v1/inventory/',
                'marketing': '/api/v1/marketing/',
                'notifications': '/api/v1/notifications/',
                'search': '/api/v1/search/',
                'reports': '/api/v1/reports/',
                'cms': '/api/v1/cms/',
            },
            'documentation': '/swagger/',
        })


class APIVersionView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({
            'versions': [
                {
                    'version': 'v1',
                    'status': 'stable',
                    'url': '/api/v1/',
                },
                {
                    'version': 'v2',
                    'status': 'beta',
                    'url': '/api/v2/',
                },
            ]
        })
