import time
import logging
import json
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.http import JsonResponse

logger = logging.getLogger('apps.common')


class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request._start_time = time.time()

    def process_response(self, request, response):
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            log_data = {
                'method': request.method,
                'path': request.path,
                'status': response.status_code,
                'duration': round(duration, 4),
                'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') and request.user.is_authenticated else None,
                'ip': self.get_client_ip(request),
            }
            if response.status_code >= 500:
                logger.error(f"Server Error: {json.dumps(log_data)}")
            elif response.status_code >= 400:
                logger.warning(f"Client Error: {json.dumps(log_data)}")
            elif duration > 2.0:
                logger.warning(f"Slow Request: {json.dumps(log_data)}")
            else:
                logger.info(f"Request: {json.dumps(log_data)}")
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    SLOW_REQUEST_THRESHOLD = 2.0

    def process_request(self, request):
        request._perf_start = time.time()

    def process_response(self, request, response):
        if hasattr(request, '_perf_start'):
            duration = time.time() - request._perf_start
            if duration > self.SLOW_REQUEST_THRESHOLD:
                logger.warning(
                    f"Slow request detected: {request.method} {request.path} "
                    f"took {duration:.2f}s"
                )
            response['X-Response-Time'] = f"{duration:.4f}s"
        return response


class RateLimitMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            ip = self.get_client_ip(request)
            key = f"rate_limit:anon:{ip}"
            limit = 1000
            window = 3600
        else:
            key = f"rate_limit:user:{request.user.id}"
            limit = 5000
            window = 3600

        current = cache.get(key, 0)
        if current >= limit:
            return JsonResponse({
                'success': False,
                'error': {
                    'status_code': 429,
                    'message': 'Rate limit exceeded.',
                }
            }, status=429)

        cache.set(key, current + 1, window)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


class SiteContextMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.site_settings = {
            'site_name': 'E-Commerce Store',
            'currency': 'USD',
            'tax_rate': 0.08,
            'free_shipping_threshold': 50.00,
        }


class SecurityHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response
