from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'users'

router = DefaultRouter()
router.register(r'addresses', views.AddressViewSet, basename='address')
router.register(r'payment-methods', views.PaymentMethodViewSet, basename='payment-method')

urlpatterns = [
    path('users/register/', views.RegisterView.as_view(), name='register'),
    path('users/login/', views.LoginView.as_view(), name='login'),
    path('users/logout/', views.LogoutView.as_view(), name='logout'),
    path('users/profile/', views.UserProfileView.as_view(), name='profile'),
    path('users/profile/update/', views.UserUpdateView.as_view(), name='profile-update'),
    path('users/change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('users/password-reset/', views.PasswordResetRequestView.as_view(), name='password-reset'),
    path('users/password-reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('users/activities/', views.UserActivityListView.as_view(), name='user-activities'),
    path('users/vendor-profile/', views.VendorProfileView.as_view(), name='vendor-profile'),
    path('admin/users/', views.UserListView.as_view(), name='admin-user-list'),
    path('admin/users/<uuid:pk>/', views.AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('admin/users/stats/', views.AdminUserStatsView.as_view(), name='admin-user-stats'),
    path('', include(router.urls)),
]
