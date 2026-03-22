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