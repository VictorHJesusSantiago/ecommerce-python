from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="E-Commerce API",
        default_version='v1',
        description="Full-featured E-Commerce REST API",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="api@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.products.urls')),
    path('api/v1/', include('apps.users.urls')),
    path('api/v1/', include('apps.orders.urls')),
    path('api/v1/', include('apps.cart.urls')),
    path('api/v1/', include('apps.payments.urls')),
    path('api/v1/', include('apps.inventory.urls')),
    path('api/v1/', include('apps.marketing.urls')),
    path('api/v1/', include('apps.notifications.urls')),
    path('api/v1/', include('apps.reviews.urls')),
    path('api/v1/', include('apps.search.urls')),
    path('api/v1/', include('apps.reports.urls')),
    path('api/v1/', include('apps.cms.urls')),
    path('api/v1/auth/', include('rest_framework.urls')),
    path('api/v1/auth/', include('apps.users.auth_urls')),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', TemplateView.as_view(template_name='storefront/home.html'), name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]

admin.site.site_header = 'E-Commerce Administration'
admin.site.site_title = 'E-Commerce Admin'
admin.site.index_title = 'Welcome to E-Commerce Administration'
