import math

import typing

from the_west_inner.requests_handler import requests_handler
from the_west_inner.premium import Premium
from the_west_inner.work_list import Work_list
from the_west_inner.bag import Bag
from the_west_inner.caching_decorators import cache_function_results

"""
This module contains utility functions and classes for handling items in a game. The return_items function returns a dictionary containing the items data from the server. The Items class represents a list of items and provides methods for finding an item by ID, checking if an item is craftable, and getting the name and price of an item. The isCraftable function returns True if an item is craftable, and nr_item returns the number of items in the bag. The has_automation function returns True if the player has automation premium, and get_corresponding_work_id returns the ID of the work corresponding to a given item ID.
"""

def apply_func_to_numbers(data, func):
    if isinstance(data, dict):
        for key, value in data.items():
            data[key] = apply_func_to_numbers(value, func)
    elif isinstance(data, list):
        for i in range(len(data)):
            data[i] = apply_func_to_numbers(data[i], func)
    elif isinstance(data, (float, int)):
        return func(data)
    return data


@cache_function_results(seconds=3*60*60)
def return_items(handler: requests_handler) -> dict:
    """
    Return the items data from the server.

    :param handler: A `requests_handler` object used to make requests to the server.
    :type handler: requests_handler
    :return: A dictionary containing the items data.
    :rtype: dict
    """
    data = handler.post("data", "")
    return data
class Items():
    def __init__(self, items):
        """
        Initialize an `Items` object with a list of item dictionaries.

        :param items: A list of dictionaries containing information about the items.
        :type items: List[dict]
        """
        self.items = {f'{x["item_id"]}': x for x in items}
        self.recipes = {x["item_id"]: x for x in items if x["type"] == "recipe"}
    def _add_to_items(self,item_id:str,item_dict:dict) -> None:
        self.items[item_id] = item_dict
    def _create_new_item(self,item_dict:dict,power:int,new_id:str) ->dict:
        upgrade_func= lambda x : (1 + 0.1*power) * x
        if power > 5 :
            raise Exception("Too much of an upgrade !")
        item_dict['speed'] = apply_func_to_numbers(data= item_dict['speed'],
                                                   func = upgrade_func )
        item_dict['bonus'] = apply_func_to_numbers(data= item_dict['bonus'],
                                                   func = upgrade_func )
        item_dict['name'] = f"{item_dict['name']}^{power}"
        item_dict['item_id'] = int(new_id)
        return item_dict
    def find_item(self, item_id: int) -> dict:
        """
        Find an item with the given ID.

        :param item_id: The ID of the item to find.
        :type item_id: int
        :return: A dictionary containing information about the item with the specified ID.
        :rtype: dict
        """
        for item in self.items.values():
            if item["item_id"] == item_id:
                return item
#    def get_item(self, item_id: int) -> dict:
#        """
#        Gets an item with the given ID.
#
#        :param item_id: The ID of the item to find.
#        :type item_id: int,str
#        :return: A dictionary containing information about the item with the specified ID.
#        :rtype: dict
#        """
#        upgraded_item = False
#        
#        item_id_string = f"{item_id }"
#        
#        if item_id_string[-1] != "0" :
#            item_id_string = item_id_string[:-1] + "0"
#            upgraded_item = True
#        
#        if item_id_string not in self.items :
#            raise Exception(f"Could not find item in the item list! : {item_id_string}")
#        
#        if upgraded_item:
#            return_upgraded_dict = self.items[item_id_string]
#            return_upgraded_dict["item_id"] = f"{item_id }"
#            return return_upgraded_dict
#        return self.items[item_id_string]
    def get_item(self, item_id :int) -> dict:
        item_id_string = f"{item_id }"
        
        if item_id_string[-1] != "0" and item_id_string not in self.items:
            base_item_id_string = item_id_string[:-1] + "0"
            if base_item_id_string not in self.items :
                raise Exception(f"Could not find item in the item list! : {item_id_string}")
            base_item_dict = self.items[base_item_id_string]
            
            new_item_dict = self._create_new_item(
                                                item_dict= base_item_dict.copy(),
                                                power = int(item_id_string[-1]),
                                                new_id = item_id_string
                                                )
            self._add_to_items(
                            item_id = item_id_string,
                            item_dict = new_item_dict
                            )
            #print(f"created new item : {item_id_string}")
        return self.items[item_id_string]
            
    def is_craftable(self, item_id: int) -> bool:
        """
        Check if an item is craftable.

        :param item_id: The ID of the item to check.
        :type item_id: int
        :return: True if the item is craftable, False otherwise.
        :rtype: bool
        """
        for item in self.items.values():
            if "craftitem" in item and item["craftitem"] == item_id:
                return True
        return False

    def is_craftable_by_id(self, item_id: int) -> int:
        """
        Check if an item is craftable by a given profession ID.

        :param item_id: The ID of the item to check.
        :type item_id: int
        :return: The profession ID that can craft the item, or None if the item is not craftable.
        :rtype: int
        """
        for item in self.items.values():
            if item["craftitem"] == item_id:
                return item["profession_id"]
    def is_consummable_item(self,item_id:int)->bool:
        """
        Check if an item is consummable and therefore can not be equipped
        
        :param item_id: The ID of the item to check.
        :type item_id: int
        :return: True if the item is consummable, False otherwise.
        :rtype: bool
        """
        return 'usetype' in self.items[item_id] and self.items[item_id]['usetype'] == "use"
    def name(self, item_id : int) -> str:
        """
        Get the name of the item.

        :return: The name of the item.
        :rtype: str
        """
        return self.get_item(item_id=item_id).get('name')

    def price(self) -> int:
        """
        Get the price of the item.

        :return: The price of the item.
        :rtype: int
        """
        return self.get_item()
    def __contains__(self,item_id:typing.Union[int,str]) -> bool:
        """
        Checks if the ID of specified item exists in the item pool.
        Args:
            item_id (int): The ID of the item to check for.
        Returns:
            bool: True if specified item exists, False otherwise.
        """
        item_id_string = f"{item_id }"
        
        if item_id_string[-1] != "0" and item_id_string not in self.items:
            base_item_id_string = item_id_string[:-1] + "0"
            if base_item_id_string not in self.items :
                raise Exception(f"Could not find item in the item list! : {item_id_string}")
            base_item_dict = self.items[base_item_id_string]
            
            new_item_dict = self._create_new_item(
                                                item_dict= base_item_dict.copy(),
                                                power = int(item_id_string[-1]),
                                                new_id = item_id_string
                                                )
            self._add_to_items(
                            item_id = item_id_string,
                            item_dict = new_item_dict
                            )
        return item_id_string in self.items
    def get_droppable_items(self) -> list:
        return [x for x in self.items.values() if x['dropable']]

def isCraftable(id_item,item_list:Items):
    return item_list.is_craftable(id_item)
def nr_item(bag:Bag,id_item):
    return bag.get_item_count(id_item)
def has_automation(premium_data:Premium):
    return premium_data.automation
def get_corresponding_work_id(id_item,work_list:Work_list):
    id_lista_munci = work_list.work_products()
    if str(id_item) not in id_lista_munci:
        return False
    munci = id_lista_munci[f"{id_item}"]
    return munci["id"]

