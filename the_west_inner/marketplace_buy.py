"""
This module contains functions for interacting with the marketplace in a game.

Classes:

Marketplace_categories: An enumeration of the different categories of items available in the marketplace.
Functions:

search_marketplace_category: Searches a given category of items in the marketplace using a provided request handler.
search_marketplace_item: Searches for a specific item in the marketplace using a provided request handler.
"""

from enum import Enum
import typing
import time
import datetime

from requests_handler import requests_handler
from items import Items
from misc_scripts import server_time


class Marketplace_categories(Enum):
    BELT = "belt"
    BODY = "body"
    RIGHT_ARM = "right_arm"
    HEAD = "head"
    LEFT_ARM = "left_arm"
    NECK = "neck"
    PANTS = "pants"
    YIELD = "yield"
    RECIPE = "recipe"
    ANIMAL = "animal"
    FOOT = "foot"

def search_marketplace_category(category:Marketplace_categories,handler:requests_handler) ->list[int]:
    """
    This function searches the given category of items in the marketplace using the given request handler.

    Args:
    category (Marketplace_categories): The category of items to search in the marketplace.
    handler (requests_handler): The request handler to use for sending the request.

    Returns:
    Optional[List[str]]: The list of items in the category, if found. Otherwise, None.
    """
    result = handler.post(window="building_market",action="search_accordion",payload={"pattern":"","type": f"{category.value}"},use_h=True)
    if result["error"] == True:
        raise Exception("Could not search category of items")
    return result["items"]

def search_marketplace_item(item_id:int,handler:requests_handler) :
    """
    This function searches the given item in the marketplace using the given request handler.

    Args:
    item_id (int): The id of the item to search in the marketplace.
    handler (requests_handler): The request handler to use for sending the request.

    Returns:
    Optional[str]: The item details, if found. Otherwise, None.
    """
    result = handler.post(window="building_market",action="search",payload={
        "item_id": f"{item_id}",
        "page": "1",
        "nav": "first",
        "sort": "bid",
        "order": "asc"
        },use_h=True)
    if result["error"] :
        return None
    return result["msg"]["search_result"]

class Marketplace_offer():
    """
    This class represents an offer on the marketplace.
    """

    def __init__(self, dict_offer: dict):
        """
        Initializes the marketplace offer with the given data.

        Args:
        dict_offer (dict): The dictionary containing the data for the offer.
        """
        self.dict_offer = dict_offer

    def is_expired(self, handler: requests_handler) -> bool:
        """
        This function checks if the offer is expired.

        Args:
        handler (requests_handler): The request handler to use for sending requests.

        Returns:
        bool: True if the offer is expired, False otherwise.
        """
        return  datetime.datetime.strptime(time.ctime(float(self.dict_offer["auction_end_date"])),"%c") < server_time(handler=handler)

    def buy_instantly(self, handler: requests_handler) -> typing.Optional[dict]:
        """
        This function buys the offer instantly.

        Args:
        handler (requests_handler): The request handler to use for sending requests.

        Returns:
        Optional[dict]: The result of the buying if it was successful, None otherwise.
        """
        result = handler.post(window="building_market",action="bid",payload={
            "bidtype" : "0" ,
            "bid" : f"{self.dict_offer['max_price']}" ,
            "market_offer_id" : f"{self.dict_offer['market_offer_id']}"
        },use_h=True)
        if result["error"] == True:
            raise Exception("Could not buy this item")
        return result["msg"]

    def price_increase(self, item_dict: dict) -> float:
        """
        This function calculates the price increase for the given item.

        Args:
        item_dict (dict): The dictionary containing the data for the item.

        Returns:
        float: The price increase for the given item.
        """
        return (float(self.item_price / self.item_count) / item_dict["sell_price"] - 1) * 100

    @property
    def seller_id(self) -> int:
        """
        This property returns the id of the seller of this offer.

        Returns:
        int: The id of the seller of this offer.
        """
        return self.dict_offer["seller_player_id"]

    @property
    def item_count(self) -> int:
        """
        This property returns the number of items in this offer.

        Returns:
        int: The number of items in this offer.
        """
        return self.dict_offer["item_count"]

    @property
    def item_price(self) -> float:
        """
        This property returns the price of the items in this offer.

        Returns:
        float: The price of the items in this offer.
        """
        return self.dict_offer["max_price"]

    @property
    def town_id(self) -> int:
        """
        This property returns the id of the town where this offer was created.

        Returns:
        int: The id of the town where this offer was created.
        """
        return self.dict_offer["market_town_id"]

    @property
    def sell_offer_completed_100_trust(self) -> bool:
        """
        This property checks if the sell offer is completed with 100% trust.

        Returns:
        bool: True if the sell offer is completed with 100% trust, False otherwise.
        """
        if "max_price" in self.dict_offer and self.dict_offer["current_bid"] == self.dict_offer["max_price"]:
            return True
        return False

    def fetch_offer(self, handler: requests_handler) -> typing.Optional[dict]:
        """
        This function fetches the given offer.

        Args:
        handler (requests_handler): The request handler to use for sending requests.

        Returns:
        Optional[dict]: The result of the fetching if it was successful, None otherwise.
        """
        fech_response = handler.post(window="building_market",
                                     action="fetch",
                                     payload={ 'market_offer_id':f'{self.dict_offer["market_offer_id"]}'},
                                     use_h=True)
        if fech_response["error"] == True:
            raise Exception("Could not fetch this offer")
        return fech_response["msg"]
class Marketplace_offer_list():
    def __init__(self, offer_list: typing.List[Marketplace_offer], handler: requests_handler, items: Items):
        """
        This is the constructor for the `Marketplace_offer_list` class.

        Args:
        offer_list (List[Marketplace_offer]): The list of `Marketplace_offer` objects.
        handler (requests_handler): The request handler to use for sending requests.
        items (Items): The items object to use for getting item data.
        """
        self.offer_list = offer_list
        self.handler = handler
        self.items = items

    def buy_all(self) -> None:
        """
        This function buys all the offers in the list.
        """
        for offer in self.offer_list:
            offer.buy_instantly(handler= self.handler)

    def buy_all_using_procentage_increase(self, max_increase: float) -> None:
        """
        This function buys all the offers in the list that have a percentage increase below the specified maximum.

        Args:
        max_increase (float): The maximum percentage increase to consider when buying.
        """
        for offer in self.offer_list:
            if offer.price_increase < max_increase:
                offer.buy_instantly(self.handler)

    def buy_first_in_list(self) -> None:
        """
        This function buys the first offer in the list.
        """
        for offer in self.offer_list:
            offer.buy_instantly(self.handler)
            break
    # make this class iterable
    def __iter__(self):
        for offer in self.offer_list:
            yield offer

    def __next__(self):
        return self.offer_list.__next__()
    
    def __len__(self):
        return len(self.offer_list)

def marketplace_buy_offer_builder(offer_dict_list:list[dict],handler:requests_handler,items:Items) ->Marketplace_offer_list:
    offer_list = []
    for offer_dict in offer_dict_list:
        offer_list.append(Marketplace_offer(dict_offer = offer_dict))
    return Marketplace_offer_list(offer_list=offer_list,
                                  handler= handler,
                                  items = items
                                  )
class ItemNotFoundException(Exception):
    pass
class ItemNotValidException(Exception):
    pass

class Marketplace_buy_manager():
    
    def __init__(self,handler:requests_handler,items:Items):
        self.handler = handler
        self.items = items
    
    def _is_on_market(self,item_id:int) -> bool:
        if item_id not in self.items:
            raise ItemNotValidException(f"The required item : {item_id} is not a valid item.")
        item_type = self.items.get_item(item_id = item_id)
        return item_id in search_marketplace_category(category = item_type,handler = self.handler)
    
    def _search_item(self,item_id:int) ->Marketplace_offer_list:
        
        raw_item_offer_list = search_marketplace_item(item_id = item_id,handler = self.handler)
        return marketplace_buy_offer_builder(offer_dict_list = raw_item_offer_list)
    
    def buy_cheapest_marketplace_item(self,item_id:int):
        offer_list = self._search_item(item_id = item_id)
        
        if len(offer_list) != 0 :
            offer_list.buy_first_in_list()
        else:
            raise ItemNotFoundException(f"No item found :{item_id}")
    
    def buy_cheapest_and_pick_up(self,item_id:int):
        self.buy_cheapest_marketplace_item(item_id= item_id)
        raise NotImplementedError("The collect item from marketplace functionality is not implemented yet!")
