from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from .models import Address, PaymentMethod, VendorProfile, UserActivity

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'password_confirm', 'phone_number']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        from apps.common.signals import user_registered
        user_registered.send(sender=User, user=user)
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    orders_count = serializers.SerializerMethodField()
    default_address = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'phone_number', 'avatar', 'date_of_birth', 'gender', 'role',
            'is_email_verified', 'newsletter_subscribed', 'loyalty_points',
            'total_spent', 'total_orders', 'orders_count', 'default_address',
            'referral_code', 'created_at',
        ]
        read_only_fields = ['id', 'email', 'role', 'loyalty_points', 'total_spent', 'total_orders', 'created_at']

    def get_orders_count(self, obj):
        return obj.total_orders

    def get_default_address(self, obj):
        address = obj.addresses.filter(is_default=True).first()
        if address:
            return AddressSerializer(address).data
        return None


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'avatar', 'date_of_birth', 'gender', 'newsletter_subscribed']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate_old_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value, is_active=True).exists():
            raise serializers.ValidationError('No active user with this email.')
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': 'Passwords do not match.'})
        return attrs


class AddressSerializer(serializers.ModelSerializer):
    full_address = serializers.CharField(read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Address
        fields = [
            'id', 'label', 'first_name', 'last_name', 'company',
            'address_line1', 'address_line2', 'city', 'state',
            'postal_code', 'country', 'phone', 'is_default',
            'is_billing', 'is_shipping', 'full_address', 'full_name',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AddressListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'label', 'city', 'state', 'country', 'is_default']


class PaymentMethodSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(read_only=True)

    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'payment_type', 'provider', 'last_four', 'is_default',
            'expiry_month', 'expiry_year', 'cardholder_name', 'display_name',
            'created_at',
        ]
        read_only_fields = ['id', 'last_four', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        if 'token' not in validated_data:
            validated_data['token'] = ''
        return super().create(validated_data)


class VendorProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = VendorProfile
        fields = [
            'id', 'user_email', 'shop_name', 'shop_description', 'shop_logo',
            'shop_banner', 'is_approved', 'commission_rate', 'total_sales',
            'total_products', 'rating', 'tax_id', 'business_type', 'website',
            'shipping_policy', 'return_policy', 'avg_processing_time',
            'created_at',
        ]
        read_only_fields = ['id', 'is_approved', 'approved_at', 'total_sales', 'total_products', 'rating', 'created_at']


class UserActivitySerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = UserActivity
        fields = ['id', 'action', 'action_display', 'description', 'metadata', 'ip_address', 'created_at']
        read_only_fields = fields


class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role', 'is_active', 'is_email_verified', 'created_at']


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'role', 'is_active',
            'is_staff', 'is_superuser', 'is_email_verified', 'phone_number',
        ]
        read_only_fields = ['email']
