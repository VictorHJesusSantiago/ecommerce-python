from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'users_auth'

urlpatterns = [
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
