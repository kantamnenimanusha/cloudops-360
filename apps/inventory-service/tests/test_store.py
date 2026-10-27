import pytest

from app.store import InsufficientStock, Store, UnknownSku


def test_list_has_items():
    assert len(Store().list()) == 3


def test_reserve_reduces_stock():
    s = Store()
    assert s.reserve("SKU-1001", 10) == {"sku": "SKU-1001", "reserved": 10, "remaining": 90}
    assert s.get("SKU-1001")["stock"] == 90


def test_reserve_unknown_sku():
    with pytest.raises(UnknownSku):
        Store().reserve("NOPE", 1)


def test_reserve_insufficient():
    with pytest.raises(InsufficientStock):
        Store().reserve("SKU-1003", 6)


def test_reserve_invalid_quantity():
    with pytest.raises(ValueError):
        Store().reserve("SKU-1001", 0)
