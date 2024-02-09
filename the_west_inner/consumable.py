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

    def _add_result_dict(self, box_session_dict: dict[int, int], update: dict[int, int]) -> dict[int, int]:
        """
        Add the counts from the 'update' dictionary to the 'box_session_dict'.
    
        Args:
            box_session_dict (dict): The main dictionary to update.
            update (dict): The dictionary containing counts to add.
    
        Returns:
            dict: The updated 'box_session_dict'.
        """
        for key, value in update.items():
            # Update counts for each key in 'update'
            if key in box_session_dict:
                box_session_dict[key] += value
            else:
                box_session_dict[key] = value
    
        return box_session_dict
    
    def _add_result_dict_iterator(self, result_dict_iterator: typing.Iterable):
        """
        Iterate through a collection of dictionaries and accumulate their counts.
    
        Args:
            result_dict_iterator (Iterable): An iterable containing dictionaries with counts.
    
        Returns:
            dict: The accumulated dictionary with combined counts.
        """
        new_dict = {}
        for result_dict in result_dict_iterator:
            # Update 'new_dict' by adding counts from each result_dict
            new_dict = self._add_result_dict(new_dict, result_dict)
    
        return new_dict
    
    def _extract_box_result_dict(self, raw_data: list) -> dict[int, int]:
        """
        Extract and process the lottery result data from the raw data.
    
        Args:
            raw_data (list): Raw data containing lottery results.
    
        Returns:
            dict[int, int]: Processed dictionary with item IDs and their corresponding counts.
        """
        # Helper function to convert raw_dict into a dictionary of item IDs and their counts
        def get_dict(raw_dict: dict) -> dict:
            loaded_dict = {}
            items = raw_dict.get('items', {})
    
            for item in items:
                item_id = item.get('item_id')
                item_count = item.get('count')
    
                # Update 'loaded_dict' by adding counts for each item
                loaded_dict = self._add_result_dict(loaded_dict, {item_id: item_count})
    
            return loaded_dict
    
        # Filter out dictionary items with 'type' key present and having value 'lottery' or 'content'
        lottery_result_dict_filter = filter(lambda x: x.get('type', None) in ['lottery','content'], raw_data)
    
        # Apply get_dict to each filtered dictionary to get processed dictionaries
        lottery_result_dict = map(get_dict, lottery_result_dict_filter)
    
        # Combine processed dictionaries into a single dictionary using _add_result_dict_iterator
        return self._add_result_dict_iterator(result_dict_iterator=lottery_result_dict)      
    def _open_box(self, box_id: int, time_sleep: int = None):
        """
        Open a box with the specified ID, process the result, and update the player's bag.

        Args:
            box_id (int): The ID of the box to open.
            time_sleep (int): Optional sleep time in seconds after opening the box. Defaults to None.

        Returns:
            dict[int, int]: Processed dictionary with item IDs and their corresponding counts obtained from opening the box.
        """
        # Use the consumable with the specified box ID and retrieve the result
        result = self._use_consumable(consumable_id=box_id)['msg']
        
        # Update the cooldown based on the result's cooldown information
        self._update_cooldown(new_cooldown_raw_date=result['cooldown'])
        
        # Extract changes and reverse them for proper handling
        changes: list = result['changes']
        changes.reverse()
        
        # Handle buy/sell changes in the player's bag
        self.bag.handle_buy_sell_changes(changes=changes)
        
        # Introduce a sleep delay if time_sleep is provided
        if time_sleep is not None:
            time.sleep(time_sleep)
        
        # Extract and process the effects of opening the box
        return self._extract_box_result_dict(raw_data=result['effects'])

    def open_box(self, box_id: int, number: int = 1):
        """
        Open a specified number of boxes and accumulate the results.

        Args:
            box_id (int): The ID of the box to open.
            number (int): The number of boxes to open. Defaults to 1.

        Returns:
            dict[int, int]: Accumulated dictionary with combined counts of items obtained from opening the boxes.
        """
        # Use a generator expression to open the box 'number' times and accumulate the results
        opening_results = (self._open_box(box_id=box_id, time_sleep=1) for _ in range(number))

        # Combine results into a single dictionary using _add_result_dict_iterator
        return self._add_result_dict_iterator(result_dict_iterator=opening_results)