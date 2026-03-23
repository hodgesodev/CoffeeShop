from drink import Drink

class Order:
    def __init__(self):
        self._price: int = 0
        self._drinks: dict[Drink, int] = {} # Drink: Count

    def update_price(self):
        price = 0
        for drink in self._drinks:
            price += drink._price * self._drinks[drink]

        self._price = price

    def add_drink(self, drink: Drink):
        if drink not in self._drinks.keys():
            self._drinks[drink] = 1
        else:
            self._drinks[drink] += 1

        self.update_price()

    def remove_drink(self, drink: Drink):
        if drink in self._drinks.keys():
            self._drinks[drink] -= 1

            if self._drinks[drink] == 0:
                self._drinks.pop(drink)
        else:
            print('drink not found')

        self.update_price()

    def get_price(self):
        price = self._price
        return price

    def get_drinks(self):
        drinks = self._drinks
        return drinks
