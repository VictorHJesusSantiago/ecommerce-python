import pytest
from decimal import Decimal
from apps.inventory.models import Warehouse, StockItem, StockMovement


@pytest.mark.django_db
class TestWarehouseModel:
    def test_warehouse_creation(self):
        warehouse = Warehouse.objects.create(
            name='Main Warehouse',
            code='WH001',
        )
        assert warehouse.name == 'Main Warehouse'
        assert warehouse.code == 'WH001'


@pytest.mark.django_db
class TestStockItemModel:
    def test_stock_adjustment(self, product):
        warehouse = Warehouse.objects.create(name='Main', code='WH001')
        stock = StockItem.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=100,
        )
        old_qty, new_qty = stock.adjust_stock(20, reason='Restocked')
        assert old_qty == 100
        assert new_qty == 120

    def test_available_quantity(self, product):
        warehouse = Warehouse.objects.create(name='Main', code='WH001')
        stock = StockItem.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=100,
            reserved_quantity=20,
        )
        assert stock.available_quantity == 80

    def test_low_stock_detection(self, product):
        warehouse = Warehouse.objects.create(name='Main', code='WH001')
        stock = StockItem.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=3,
            low_stock_threshold=5,
        )
        assert stock.is_low_stock is True

    def test_reserve_stock(self, product):
        warehouse = Warehouse.objects.create(name='Main', code='WH001')
        stock = StockItem.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=100,
        )
        result = stock.reserve_stock(10)
        assert result is True
        assert stock.reserved_quantity == 10

    def test_reserve_insufficient_stock(self, product):
        warehouse = Warehouse.objects.create(name='Main', code='WH001')
        stock = StockItem.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=5,
        )
        result = stock.reserve_stock(10)
        assert result is False
