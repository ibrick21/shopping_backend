from typing import Protocol

class InventoryProtocol(Protocol):
    def add_stock(self, product: str, quantity: int):
        ...

    def decrease_stock(self, product: str, quantity: int):
        ...