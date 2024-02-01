import time
import typing
import datetime
from requests_handler import requests_handler
from misc_scripts import server_time,wait_until_date,wait_until_date_callback
from bag import Bag

"""
This module contains classes for handling consumable items in a game. The `Cooldown` class represents a cooldown period, and the `ConsumableHandler` class is used to use consumable items, update the bag and cooldown, and wait until the cooldown period has passed.
"""

class Cooldown:
    """
    This class represents a cooldown period.

    Attributes:
        handler (requests_handler): A request handler.
        cooldown_date (datetime): The date when the cooldown period ends.
    """

    def __init__(self, handler: requests_handler, cooldown_date: datetime):
        """
        Initializes a Cooldown instance with the specified handler and cooldown date.

        Args:
            handler (requests_handler): A request handler.
            cooldown_date (datetime): The date when the cooldown period ends.
        """
        self.handler = handler
        self.cooldown_date = cooldown_date

    @property
    def cooldown_passed(self) -> bool:
        """
        Returns whether the current time is greater than the cooldown date.

        Returns:
            bool: True if the current time is greater than the cooldown date, False otherwise.
        """
        return self.cooldown_date < server_time(handler=self.handler)

    @property
    def cooldown(self) -> datetime:
        """
        Returns the cooldown date.

        Returns:
            datetime: The cooldown date.
        """
        return self.cooldown_date

    def update(self, new_cooldown_date: datetime):
        """
        Updates the cooldown date with the specified new cooldown date.

        Args:
            new_cooldown_date (datetime): The new cooldown date.
        """
        self.cooldown_date = new_cooldown_date

class Consumable_handler:
    """
    This class is used to handle consumable items.

    Attributes:
        handler (requests_handler): A request handler.
        bag (Bag): An instance of the Bag class.
        cooldown (Cooldown): An instance of the Cooldown class.
    """

    def __init__(self, handler: requests_handler, bag: Bag, cooldown: Cooldown):
        """
        Initializes a Consumable_handler instance with the specified handler, bag, and cooldown.

        Args:
            handler (requests_handler): A request handler.
            bag (Bag): An instance of the Bag class.
            cooldown (Cooldown): An instance of the Cooldown class.
        """
        self.handler = handler
        self.bag = bag
        self.cooldown = cooldown

    def _use_consumable(self, consumable_id: int):
        """
        Attempts to use the specified consumable item.

        Args:
            consumable_id (int): The ID of the consumable item to use.

        Raises:
            Exception: If the item is not in the bag or if there is an error using the item.

        Returns:
            dict: The result of using the item.
        """
        if consumable_id not in self.bag:
            raise Exception("You do not have enough consumables of this type")
        result = self.handler.post(
                    window="itemuse",
                    action="use_item",
                    action_name="action",
                    payload={"item_id": f"{consumable_id}"},
                    use_h=True,
                    )
        if result["error"] == True:
            raise Exception("You could not use item")
        return result

    def _update_bag(self, item_id):
        """
        Consumes the specified item from the bag.
    
        Args:
            item_id (int): The ID of the item to consume.
        """
        self.bag.consume_item(item_id=item_id)
    
    def _update_cooldown(self, new_cooldown_raw_date: float):
        """
        Updates the cooldown with the specified raw date.
    
        Args:
            new_cooldown_raw_date (float): The new raw date to set the cooldown to.
        """
        game_time = datetime.datetime.strptime(
            time.ctime(float(new_cooldown_raw_date)), "%c"
        )
        self.cooldown.update(new_cooldown_date=game_time)
    
    def use_consumable(self, consumable_id: int,function_callback:typing.Callable=None,*args,**kwargs):
        """
        Uses the specified consumable item if the cooldown has passed,
        and updates the bag and cooldown.
    
        Args:
            consumable_id (int): The ID of the consumable item to use.
        """
        if not self.cooldown.cooldown_passed:
            wait_until_date_callback(self.cooldown.cooldown, self.handler,callback_function=function_callback,*args,**kwargs)
        new_cooldown = self._use_consumable(consumable_id=consumable_id)["msg"]["cooldown"]
        self._update_cooldown(new_cooldown_raw_date=new_cooldown)
        self._update_bag(consumable_id)