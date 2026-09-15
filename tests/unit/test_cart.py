import pytest
from decimal import Decimal
from apps.cart.models import Cart, CartItem


@pytest.mark.django_db
class TestCartModel:
    def test_cart_subtotal(self, cart, product):
        cart.add_item(product, quantity=3)
        assert cart.subtotal == Decimal('89.97')

    def test_cart_total_items(self, cart, product):
        cart.add_item(product, quantity=5)
        assert cart.total_items == 5

    def test_cart_clear(self, cart, product):
        cart.add_item(product, quantity=2)
        cart.clear()
        assert cart.items.count() == 0

    def test_cart_add_existing_item(self, cart, product):
        cart.add_item(product, quantity=2)
        cart.add_item(product, quantity=3)
        item = cart.items.first()
        assert item.quantity == 5

    def test_cart_remove_item(self, cart, product):
        item = cart.add_item(product, quantity=1)
        cart.remove_item(item.pk)
        assert cart.items.count() == 0


@pytest.mark.django_db
class TestCartItemModel:
    def test_line_total(self, cart, product):
        item = cart.add_item(product, quantity=3)
        assert item.line_total == Decimal('89.97')

    def test_unit_price(self, cart, product):
        item = cart.add_item(product, quantity=1)
        assert item.unit_price == Decimal('29.99')
