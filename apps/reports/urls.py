from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'reports'

router = DefaultRouter()
router.register(r'reports', views.ReportViewSet, basename='report')
router.register(r'analytics', views.AnalyticsEventViewSet, basename='analytics')
router.register(r'daily-stats', views.DailyStatsViewSet, basename='daily-stats')
router.register(r'product-performance', views.ProductPerformanceViewSet, basename='product-performance')
router.register(r'sales-forecasts', views.SalesForecastViewSet, basename='sales-forecast')

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('', include(router.urls)),
]
