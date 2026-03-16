from ingredient import Ingredient

class Drink:
    def __init__(self):
        self._price: int = 0
        self._ingredients: dict[Ingredient, int] = {}   # IngredientObject: Quantity

    def add_ingredient(self, ingredient: Ingredient):
        if ingredient not in self._ingredients:
            self._ingredients[ingredient] = 1
        else:
            self._ingredients[ingredient] += 1

        self.update_price()

    def remove_ingredient(self, ingredient: Ingredient):
        if ingredient in self._ingredients:
            self._ingredients[ingredient] -= 1
            if self._ingredients[ingredient] == 0:
                self._ingredients.pop(ingredient)

        else:
            print("ingredient not found")

        self.update_price()

    def update_price(self):
        price = 0
        for ingredient in self._ingredients:
            price += ingredient.get_price() * self._ingredients[ingredient]

        self._price = price

    def get_ingredients(self):
        ingredients = self._ingredients
        return ingredients

    def get_price(self):
        price = self._price
        return price