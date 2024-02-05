"""
This module contains a class that represents a bag that can hold items. The bag has the following functionality:
- Initialization with a dictionary that maps item IDs to their counts in the bag
- Accessing the count of a specific item in the bag
- Checking if the bag contains a specific item
- Removing an item from the bag
- Consuming a specific amount of an item from the bag
"""
import typing

class Bag():
    def __init__(self,item_dict:typing.Dict):
        self.item_dict = {x["item_id"]:x["count"] for x in item_dict}
    def __getitem__(self, item_id: int) -> int:
        """
        Returns the count of the specified item in the bag.
        Args:
            item_id (int): The ID of the item to get the count of.
        Returns:
            int: The count of the specified item in the bag.
        """
        return self.item_dict.get(item_id, 0)
    def __contains__(self, item_id: int) -> bool:
        """
        Checks if the bag contains the specified item.
        Args:
            item_id (int): The ID of the item to check for.
        Returns:
            bool: True if the bag contains the specified item, False otherwise.
        """
        return item_id in self.item_dict
    def _remove_item(self, item_id: int) -> bool:
        """
        Removes the specified item from the bag.
        Args:
            item_id (int): The ID of the item to remove.
        Returns:
            bool: True if the item was removed, False if the item was not in the bag.
        """
        if item_id not in self.item_dict:
            return False
        self.item_dict.pop(item_id)
        return True

    def consume_item(self, item_id: int, amount: int = 1):
        """
        Consumes the specified amount of the specified item from the bag.
        Args:
            item_id (int): The ID of the item to consume.
            amount (int): The number of items to consume.
        Raises:
            Exception: If the specified amount is greater than the number of items in the bag.
        """
        if item_id == None :
            return False
        if amount == self.item_dict[item_id]:
            self._remove_item(item_id=item_id)
        elif amount < self.item_dict[item_id]:
            self.item_dict[item_id] -= amount
        else:
            raise Exception("Invalid amount")
    def add_item(self, item_id:int,amount : int = 1):
        """
        Adds a specified number of the specified item to the bag
        Args:
            item_id (int): The ID of the item to add.
            amount (int): The number of items to add.
        """
        if item_id == None :
            return False
        if item_id in self.item_dict :
            self.item_dict[item_id] += amount
        else:
            self.item_dict[item_id] = amount
    def add_item_dict(self,item_dict : dict[int,int]):
        for item_id,item_number in item_dict.items():
            
            self.add_item(item_id = item_id,amount = item_number)