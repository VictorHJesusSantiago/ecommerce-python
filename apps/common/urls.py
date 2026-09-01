from django.urls import path
from . import views

app_name = 'common'

urlpatterns = [
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
    path('meta/', views.APIMetaView.as_view(), name='api-meta'),
    path('versions/', views.APIVersionView.as_view(), name='api-versions'),
]
