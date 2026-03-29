from drink import Drink

class Order:
    def __init__(self):
        self._price: float = 0.0
        self._drinks: dict[tuple[Drink, str], int] = {}  # (Drink, size_name): count

    def update_price(self):
        price = 0.0
        for (drink, _size), count in self._drinks.items():
            price += drink.get_price() * count
        self._price = price

    def add_drink(self, drink: Drink, size: str):
        key = (drink, size)
        self._drinks[key] = self._drinks.get(key, 0) + 1
        self.update_price()

    def remove_drink(self, drink: Drink, size: str):
        key = (drink, size)
        if key not in self._drinks:
            print(f"Drink '{drink.get_name()}' (size: {size}) not found in order")
            return

        self._drinks[key] -= 1
        if self._drinks[key] == 0:
            del self._drinks[key]

        self.update_price()

    def get_price(self) -> float:
        return self._price

    def get_drinks(self) -> dict[tuple[Drink, str], int]:
        return self._drinks