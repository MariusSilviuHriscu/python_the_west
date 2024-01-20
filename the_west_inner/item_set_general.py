import typing
from requests_handler import requests_handler

class IntString(str):
    def __new__(cls, value: str):
        try:
            int(value)
        except ValueError:
            raise ValueError(f"{value} is not a valid integer")
        return super().__new__(cls, value)

Set_bonus_dict = typing.Dict[IntString,typing.List]
    
class Item_set():
    """
    Represents an item set with a key, name, list of items, and bonus dictionary
    """
    def __init__(self, key: str, name: str, list_items: typing.List[int], bonus_dict: Set_bonus_dict):
        self.key = key
        self.name = name
        self.list_items = list_items
        self.bonus_dict = bonus_dict
    
    def __str__(self) -> str:
        """
        Returns a string representation of the item set's key
        """
        return self.key

class Item_sets():
    """
    Represents a collection of item sets with a dictionary mapping set keys to set instances
    """
    def __init__(self, set_list: typing.List[Item_set]):
        """
        Initializes an Item_sets instance with a list of Item_set instances
        """
        self.set_list = {x.key : x for x in set_list}
    
    def __getitem__(self, set_key: str) -> Item_set:
        """
        Returns the Item_set instance with the given key, or raises an Exception if not found
        """
        if set_key not in self.set_list:
            raise Exception(f"Can't find the correct set! : {set_key}")
        
        return self.set_list[set_key]
    
    def __str__(self) -> str:
        """
        Returns a string representation of the set_list dictionary
        """
        return f"{self.set_list}"
    
    def __repr__(self) -> str:
        """
        Returns a string representation of the set_list dictionary
        """
        return self.__str__()

def get_item_sets(requests_handler: requests_handler) -> Item_sets:
    """
    Retrieves a list of item sets from a requests_handler object and returns an Item_sets instance
    
    Args:
        requests_handler: An object that provides access to a remote data source
    
    Returns:
        An Item_sets instance initialized with the list of item sets retrieved from the data source
    """
    # Retrieve a list of item sets from the data source
    set_list = requests_handler.post(window="data", action="item_sets", action_name="mode")
    # Create a list of Item_set instances from the retrieved data
    item_sets = [Item_set(
                        key=x['key'],
                        name=x['name'],
                        list_items=[y*1000 for y in x['items']],
                        bonus_dict=x['bonus']
                        )
                 for x in set_list]
    # Return an Item_sets instance initialized with the list of item sets
    return Item_sets(set_list=item_sets)