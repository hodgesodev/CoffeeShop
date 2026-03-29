from drink import Drink


class Order:
    def __init__(self):
        self._price: float = 0.0
        self._drinks: dict[tuple[Drink, str], int] = {}  # (Drink, size_name): count
        self._unit_prices: dict[tuple[Drink, str], float] = {}  # (Drink, size_name): unit price

    def update_price(self):
        self._price = sum(
            self._unit_prices[key] * count
            for key, count in self._drinks.items()
        )

    def add_drink(self, drink: Drink, size: str, unit_price: float):
        key = (drink, size)
        self._drinks[key] = self._drinks.get(key, 0) + 1
        self._unit_prices[key] = unit_price
        self.update_price()

    def remove_drink(self, drink: Drink, size: str):
        key = (drink, size)
        if key not in self._drinks:
            print(f"Drink '{drink.get_name()}' (size: {size}) not found in order")
            return

        self._drinks[key] -= 1
        if self._drinks[key] == 0:
            del self._drinks[key]
            del self._unit_prices[key]

        self.update_price()

    def get_price(self) -> float:
        return self._price

    def get_drinks(self) -> dict[tuple[Drink, str], int]:
        return self._drinks

    def get_unit_price(self, drink: Drink, size: str) -> float:
        return self._unit_prices.get((drink, size), 0.0)

    def __repr__(self):
        return f"Order(price={self._price:.2f}, drinks={self._drinks})"