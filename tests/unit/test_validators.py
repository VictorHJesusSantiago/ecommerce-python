import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from apps.common.validators import (
    PhoneNumberValidator, PriceValidator, SKUValidator,
    StrongPasswordValidator, QuantityValidator
)


class TestPhoneNumberValidator:
    def test_valid_phone(self):
        validator = PhoneNumberValidator()
        validator('+1234567890')

    def test_invalid_phone(self):
        validator = PhoneNumberValidator()
        with pytest.raises(ValidationError):
            validator('123')


class TestPriceValidator:
    def test_valid_price(self):
        validator = PriceValidator()
        validator(Decimal('10.00'))

    def test_price_too_low(self):
        validator = PriceValidator()
        with pytest.raises(ValidationError):
            validator(Decimal('0.00'))


class TestSKUValidator:
    def test_valid_sku(self):
        validator = SKUValidator()
        validator('ABC123')

    def test_invalid_sku(self):
        validator = SKUValidator()
        with pytest.raises(ValidationError):
            validator('a')


class TestStrongPasswordValidator:
    def test_strong_password(self):
        validator = StrongPasswordValidator()
        validator('StrongP@ss1')

    def test_weak_password(self):
        validator = StrongPasswordValidator()
        with pytest.raises(ValidationError):
            validator('weak')


class TestQuantityValidator:
    def test_valid_quantity(self):
        validator = QuantityValidator()
        validator(5)

    def test_negative_quantity(self):
        validator = QuantityValidator()
        with pytest.raises(ValidationError):
            validator(-1)
