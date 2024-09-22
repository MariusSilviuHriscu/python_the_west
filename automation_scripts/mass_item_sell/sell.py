import time
import typing
from the_west_inner.bag import Bag
from the_west_inner.currency import Currency
from the_west_inner.traveling_merchant import Travelling_merchant_manager
from the_west_inner.items import Items


class SellOrder:
    """
    Represents an order to sell a specific item.

    Attributes:
        item_id (int): The unique identifier for the item to be sold.
        item_price (int): The price at which the item will be sold.
        item_number (int): The quantity of the item to be sold. Defaults to 1.
    """
    
    def __init__(self, item_id: int, item_price: int, item_number: int = 1):
        self.item_id = item_id
        self.item_number = item_number
        self.item_price = item_price
    

class SellDecisionManager:
    """
    Manages the decision-making process for selling items.

    Attributes:
        bag (Bag): The player's bag containing all items.
        items (Items): A collection of all item definitions.
        item_exception_list (list[int] | None): A list of item IDs to exclude from selling.
    
    Methods:
        decide_sell() -> typing.Generator[SellOrder, None, None]:
            Generates SellOrder objects for all eligible items in the bag.

        decide_sell_list(list_items: list[int]) -> typing.Generator[SellOrder, None, None]:
            Generates SellOrder objects for a specified list of items.
    """
    
    def __init__(self, bag: Bag, items: Items, item_exception_list: list[int] | None = None):
        self.bag = bag
        self.items = items
        self.item_exception_list = set() if item_exception_list is None else {x for x in item_exception_list}
    
    def decide_sell(self) -> typing.Generator[SellOrder, None, None]:
        """
        Determines which items should be sold based on the player's bag and criteria.

        Returns:
            typing.Generator[SellOrder, None, None]: A generator of SellOrder objects for eligible items.
        """
        
        bad_item_type = ['yield', 'recipe']
        
        sell_dict = {int(x) : y for x, y in self.items.items.items() 
                     if y.get('dropable') is True 
                     if y.get('type') not in bad_item_type 
                     if int(x) not in self.item_exception_list}
        
        for item_id, item_dict in sell_dict.items():

            number = self.bag[item_id]
            if number > 0:
                
                yield SellOrder(
                    item_id=int(item_id),
                    item_price=item_dict.get('sell_price'),
                    item_number=number
                )
    
    def decide_sell_list(self, list_items: list[int]) -> typing.Generator[SellOrder, None, None]:
        """
        Determines which items from a specific list should be sold based on the player's bag and criteria.

        Args:
            list_items (list[int]): A list of item IDs to be considered for selling.

        Returns:
            typing.Generator[SellOrder, None, None]: A generator of SellOrder objects for eligible items in the list.
        """
        
        bad_item_type = ['yield', 'recipe']
        
        sell_dict = {int(x) : y for x, y in self.items.items.items() 
                     if y.get('dropable') is True 
                     if y.get('type') not in bad_item_type 
                     if int(x) not in self.item_exception_list
                     if x in list_items}
        
        for item_id, item_dict in sell_dict.items():

            number = self.bag[item_id]
            
            if number > 0:
                
                yield SellOrder(
                    item_id=int(item_id),
                    item_price=item_dict.get('sell_price'),
                    item_number=number
                )


class SellManager:
    """
    Manages the selling of items to the traveling merchant.

    Attributes:
        travelling_merchant_manager (Travelling_merchant_manager): The manager responsible for interactions with the traveling merchant.
        currency (Currency): The player's currency handler.
        items (Items): A collection of all item definitions.
    
    Methods:
        _sell(sell_order: SellOrder) -> int:
            Executes the sale of a single item and returns the money earned.

        sell(sell_order_generator: typing.Generator[SellOrder, None, None], pause: int | None = None) -> int:
            Processes a generator of SellOrder objects and sells each item. Optionally pauses between sales.
    """
    
    def __init__(self, travelling_merchant_manager: Travelling_merchant_manager,
                 currency: Currency,
                 items: Items):
        self.travelling_merchant_manager = travelling_merchant_manager
        self.currency = currency
        self.items = items
    
    def _sell(self, sell_order: SellOrder) -> int:
        """
        Sells a single item to the traveling merchant.

        Args:
            sell_order (SellOrder): The SellOrder object containing details of the item to be sold.

        Returns:
            int: The amount of money earned from the sale.

        Raises:
            ValueError: If the money received does not match the expected amount.
        """
        
        initial_money = self.currency.total_money
        self.travelling_merchant_manager.sell_item(
            item_id=sell_order.item_id,
            amount=sell_order.item_number
        )
        if self.currency.total_money - initial_money != sell_order.item_price * sell_order.item_number:
            raise ValueError(f'You sold and got {self.currency.total_money - initial_money} instead of expected {sell_order.item_price * sell_order.item_number}')
        
        return self.currency.total_money - initial_money
    
    def sell(self, sell_order_generator: typing.Generator[SellOrder, None, None], pause: int | None = None) -> int:
        """
        Processes the sale of multiple items using a generator of SellOrder objects.

        Args:
            sell_order_generator (typing.Generator[SellOrder, None, None]): A generator that yields SellOrder objects.
            pause (int | None): An optional pause duration in seconds between each sale.

        Returns:
            int: The total amount of money earned from all sales.
        """
        
        amount = 0
        total_number = 0
        for sell_order in sell_order_generator:
            item_name = self.items.find_item(item_id=sell_order.item_id).get('name')
            print(f"Selling {item_name}: {sell_order.item_number}")
            if pause is not None:
                time.sleep(pause)
            result = self._sell(sell_order=sell_order)
            print(f'Sold for {result}')
            
            amount += result
            total_number += sell_order.item_number
        
        print('-' * 30)
        print(f'Sold {total_number} items for {amount} $')
        
        return amount
