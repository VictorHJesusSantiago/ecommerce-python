from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from .models import Address, PaymentMethod, VendorProfile, UserActivity
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    UserUpdateSerializer, ChangePasswordSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer, AddressSerializer, PaymentMethodSerializer,
    VendorProfileSerializer, UserActivitySerializer, UserListSerializer,
    AdminUserUpdateSerializer, AddressListSerializer,
)
from apps.common.permissions import IsOwner, IsAdminUser, IsVendor
from apps.common.pagination import StandardResultsSetPagination

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        UserActivity.log(user, 'login', 'Account created', ip_address=request.META.get('REMOTE_ADDR'))
        return Response({
            'success': True,
            'message': 'Registration successful.',
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request,
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        if user is None:
            return Response({
                'success': False,
                'error': {'message': 'Invalid credentials.'}
            }, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({
                'success': False,
                'error': {'message': 'Account is disabled.'}
            }, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        ip = request.META.get('REMOTE_ADDR')
        user.record_login(ip)
        UserActivity.log(user, 'login', 'Logged in', ip_address=ip)
        return Response({
            'success': True,
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        })


class LogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            UserActivity.log(request.user, 'logout', 'Logged out')
            return Response({'success': True, 'message': 'Logged out successfully.'})
        except Exception:
            return Response({'success': False, 'error': {'message': 'Invalid token.'}},
                          status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'success': True, 'user': serializer.data})


class UserUpdateView(generics.UpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'message': 'Password changed successfully.'})


class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        from apps.notifications.tasks import send_password_reset_email
        send_password_reset_email.delay(serializer.validated_data['email'])
        return Response({'success': True, 'message': 'Password reset email sent.'})


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset successful.'})


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return AddressListSerializer
        return AddressSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        address = self.get_object()
        address.is_default = True
        address.save(update_fields=['is_default'])
        return Response({'success': True, 'message': 'Default address updated.'})


class PaymentMethodViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        pm = self.get_object()
        pm.is_default = True
        pm.save(update_fields=['is_default'])
        return Response({'success': True, 'message': 'Default payment method updated.'})


class VendorProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = VendorProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsVendor]

    def get_object(self):
        profile, _ = VendorProfile.objects.get_or_create(
            user=self.request.user,
            defaults={'shop_name': f"{self.request.user.username}'s Shop"}
        )
        return profile


class UserActivityListView(generics.ListAPIView):
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return UserActivity.objects.filter(user=self.request.user)[:50]


class UserListView(generics.ListAPIView):
    serializer_class = UserListSerializer
    permission_classes = [IsAdminUser]
    pagination_class = StandardResultsSetPagination
    queryset = User.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        role = self.request.query_params.get('role')
        if role:
            qs = qs.filter(role=role)
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(email__icontains=search) | qs.filter(username__icontains=search)
        return qs


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdminUserUpdateSerializer
    permission_classes = [IsAdminUser]
    queryset = User.objects.all()

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.soft_delete()
        return Response({'success': True, 'message': 'User deleted.'})


class AdminUserStatsView(generics.GenericAPIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total = User.objects.count()
        active = User.objects.filter(is_active=True).count()
        vendors = User.objects.filter(role='vendor').count()
        customers = User.objects.filter(role='customer').count()
        verified = User.objects.filter(is_email_verified=True).count()
        return Response({
            'total_users': total,
            'active_users': active,
            'inactive_users': total - active,
            'vendors': vendors,
            'customers': customers,
            'verified_users': verified,
        })
