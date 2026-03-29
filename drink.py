class Drink:
    def __init__(self, name: str, price: float):
        self._name: str = name
        self._price: float = price

    def get_price(self):
        price = self._price
        return price

    def set_price(self, price: float):
        self._price = price

    def set_name(self, name: str):
        self._name = name

    def get_name(self):
        return self._name

    def __eq__(self, other):
        return self._name == other._name and self._price == other._price

    def __hash__(self):
        return hash((self._name, self._price))

    def __repr__(self):
        return f"Drink(name={self._name!r}, price={self._price})"
