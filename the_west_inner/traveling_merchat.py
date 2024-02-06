import typing
from dataclasses import dataclass

from currency import Currency

# Dictionary to map currency type IDs to their names
TRAVELLING_MARKET_CURRENCY_DICT = {
    1: 'bonds',
    2: 'nuggets',
    4: 'dollar',
    8: 'veteran',
    3: 'combination_type'
}

@dataclass
class Travelling_market_offer:
    currency_type_id: int
    item_id: int
    price_bonds: int
    price_dollars: int
    price_nuggets: int
    price_veteran: int

    def can_afford(self, currency: Currency, preference: int = 0, currency_type_id=None) -> bool:
        """
        Check if the player can afford the Travelling Market offer based on the provided currency.

        Args:
            currency (Currency): The player's currency.
            preference (int): The preferred currency type (for combination_type). Defaults to 0.
            currency_type_id (int): The specific currency type to check. Defaults to None.

        Returns:
            bool: True if the player can afford the offer, False otherwise.
        """

        # If currency_type_id is not provided, use the one from the offer
        if currency_type_id is None:
            currency_type_id = self.currency_type_id

        # Get the name of the currency type
        currency_type_name = TRAVELLING_MARKET_CURRENCY_DICT.get(currency_type_id, None)

        # Check affordability based on the currency type
        if currency_type_name == 'bonds':
            return self.price_bonds <= currency.oup
        elif currency_type_name == 'nuggets':
            return self.price_nuggets <= currency.nuggets
        elif currency_type_name == 'dollar':
            return self.price_dollars <= currency.total_money
        elif currency_type_name == 'veteran':
            return self.price_veteran <= currency.veteran_points
        elif currency_type_name == 'combination_type':
            # For combination_type, check affordability based on the preferred currency
            return self.can_afford(currency=currency, currency_type_id=preference)
        else:
            # Unknown currency type
            raise ValueError(f"Unknown currency type ID: {currency_type_id}")
