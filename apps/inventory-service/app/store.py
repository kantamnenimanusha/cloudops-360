"""Thread-safe in-memory stock store (stdlib only, so it is unit-testable anywhere)."""
import threading


class UnknownSku(Exception):
    pass


class InsufficientStock(Exception):
    pass


class Store:
    def __init__(self):
        self._lock = threading.Lock()
        self._items = {
            "SKU-1001": {"sku": "SKU-1001", "name": "Widget", "stock": 100},
            "SKU-1002": {"sku": "SKU-1002", "name": "Gadget", "stock": 50},
            "SKU-1003": {"sku": "SKU-1003", "name": "Gizmo", "stock": 5},
        }

    def list(self):
        with self._lock:
            return [dict(v) for v in self._items.values()]

    def get(self, sku):
        with self._lock:
            if sku not in self._items:
                raise UnknownSku(sku)
            return dict(self._items[sku])

    def reserve(self, sku, quantity):
        if quantity < 1:
            raise ValueError("quantity must be >= 1")
        with self._lock:
            item = self._items.get(sku)
            if item is None:
                raise UnknownSku(sku)
            if item["stock"] < quantity:
                raise InsufficientStock(sku)
            item["stock"] -= quantity
            return {"sku": sku, "reserved": quantity, "remaining": item["stock"]}
