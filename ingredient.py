class Ingredient:
    def __init__(self, ingredient: str, price: int):
        self._name: str = ingredient
        self._price: float = price

    def get_price(self):
        price = self._price
        return price

    def get_name(self):
        name = self._name
        return name