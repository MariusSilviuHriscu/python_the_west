"""
This module contains functions and a class for interacting with the marketplace in a game.

Functions:

search_fetch_offers: Fetches the offers in the marketplace using a provided request handler.
put_product_on_market: Puts a product on the marketplace using a provided request handler and Sell_offer_data object.
Classes:

Sell_offer_data: Represents the data required to put a product on the marketplace.
Auction_sell_manager: A manager for auctioning and selling products on the marketplace, with methods for going to the closest town, finding the best offer for a product, buying a product, and auctioning or selling a product.
"""

from requests_handler import requests_handler
from player_data import Player_data
from work_manager import Work_manager
from task_queue import TaskQueue
from items import Items
from dataclasses import dataclass
from misc_scripts import wait_until_date,orase
import typing
from marketplace_buy import Marketplace_offer,Marketplace_offer_list
from currency import Currency


def search_fetch_offers(handler:requests_handler) -> typing.Optional[str]:
    """
    This function fetches the offers in the marketplace using the given request handler.

    Args:
    handler (requests_handler): The request handler to use for sending the request.

    Returns:
    Optional[str]: The offers in the marketplace, if found. Otherwise, None.
    """
    result = handler.post(window="building_market",action="fetch_offers",payload={"page":"0"},use_h=True)
    if result["error"] == True:
        raise Exception("Could not fetch offers")
    return  result["msg"]["search_result"]

@dataclass
class Sell_offer_data:
    """
    This class represents the data required to put a product on the marketplace.
    """
    town_id : str
    item_id: str
    itemcount: str
    auctioncount: str
    sellrights: str
    auctionlength: str
    description: str
    auctionprice: str
    maxprice: str

def put_product_on_market(handler:requests_handler,sell_offer_data :Sell_offer_data) -> typing.Optional[str]:
    """
    This function puts the given product on the marketplace using the given request handler.

    Args:
    handler (requests_handler): The request handler to use for sending the request.
    sell_offer_data (Sell_offer_data): The details of the product to put on the marketplace.

    Returns:
    Optional[str]: The result of the put up request, if successful. Otherwise, None.
    """
    payload = {
            "town_id":f"{sell_offer_data.town_id}",
            "item_id": f"{sell_offer_data.item_id}",
            "itemcount": f"{sell_offer_data.itemcount}",
            "auctioncount": f"{sell_offer_data.auctioncount}",
            "sellrights": f"{sell_offer_data.sellrights}",
            "auctionlength": f"{sell_offer_data.auctionlength}",
            "description":f"{sell_offer_data.description}",
            "auctionprice": f"{sell_offer_data.auctionprice}",
            "maxprice": f"{sell_offer_data.maxprice}"
        }
    payload = {x:payload[x] for x in payload if not (x == "auctionprice" and payload[x]=="")}
    result = handler.post(window="building_market",action="putup",payload=payload,use_h=True)
    if result["error"] == True :
        raise Exception("Could not put on market")
    return result["msg"]
class Auction_sell_manager:
    """
    This class represents a manager for auctioning and selling products on the marketplace.
    """

    def __init__(self,
                 handler: requests_handler, 
                 player_data: Player_data,
                 work_manager: Work_manager,
                 task_queue: TaskQueue,
                 items: Items,
                 currency : Currency
                 ):
        """
        Initializes the auction sell manager with the given parameters.

        Args:
        handler (requests_handler): The request handler to use for sending requests.
        player_data (Player_data): The player data instance.
        work_manager (Work_manager): The work manager instance.
        task_queue (TaskQueue): The task queue instance.
        items (Items): The items instance.
        """
        self.handler = handler
        self.player_data = player_data
        self.work_manager = work_manager
        self.task_queue = task_queue
        self.items = items
        self.currency = currency
class Auction_sell_manager:
    """
    This class represents a manager for auctioning and selling products on the marketplace.
    """

    def __init__(self,
                 handler: requests_handler, 
                 player_data: Player_data,
                 work_manager: Work_manager,
                 task_queue: TaskQueue,
                 items: Items,
                 currency : Currency
                 ):
        """
        Initializes the auction sell manager with the given parameters.

        Args:
        handler (requests_handler): The request handler to use for sending requests.
        player_data (Player_data): The player data instance.
        work_manager (Work_manager): The work manager instance.
        task_queue (TaskQueue): The task queue instance.
        items (Items): The items instance.
        """
        self.handler = handler
        self.player_data = player_data
        self.work_manager = work_manager
        self.task_queue = task_queue
        self.items = items
        self.currency = currency

    def _go_to_closest_town(self) -> str:
        """
        This function moves the player to the closest town.

        Returns:
        str: The id of the closest town.
        """
        closest_town_id = orase(self.handler, self.player_data)[0]
        self.work_manager.move_to_town(closest_town_id)
        wait_until_date(wait_time= self.task_queue.get_tasks_expiration(), handler=self.handler)
        return closest_town_id

    def _create_auction(self, item_id: int, number_of_items: int, unitary_price: int, town_id: int, description: str="") -> Sell_offer_data:
        """
        This function creates an auction for the given product.

        Args:
        item_id (int): The id of the product to auction.
        number_of_items (int): The number of items to auction.
        unitary_price (int): The unitary price of the product.
        town_id (int): The id of the town where the auction will be created.
        description (str): The description of the auction. Default is an empty string.

        Returns:
        Sell_offer_data: The data for the auction.
        """
        return Sell_offer_data(
            town_id= town_id ,
            item_id = item_id ,
            itemcount = number_of_items ,
            auctioncount = "1" ,
            sellrights= "2" ,
            auctionlength= "7" ,
            description = description ,
            auctionprice= "" ,
            maxprice = number_of_items * unitary_price
        )
    def sell_in_nearest_town(self, item_id: int, number_of_items: int, unitary_price: int, description: str="") -> typing.Optional[dict]:
        """
        This function auctions and sells the given product in the nearest town.

        Args:
        item_id (int): The id of the product to auction.
        number_of_items (int): The number of items to auction.
        unitary_price (int): The unitary price of the product.
        description (str): The description of the auction. Default is an empty string.

        Returns:
        Optional[dict]: The result of the auction if it was successful, None otherwise.
        """
        town_id = self._go_to_closest_town()
        auction = self._create_auction(
            item_id= item_id ,
            number_of_items= number_of_items ,
            unitary_price = unitary_price ,
            town_id = town_id
        )
        return put_product_on_market(
            handler = self.handler,
            sell_offer_data = auction
            )

    def search_sell_offer(self) -> Marketplace_offer_list:
        """
        This function searches for the sell offers on the marketplace.

        Returns:
        Marketplace_offer_list: The list of offers on the marketplace.
        """
        return Marketplace_offer_list(
            offer_list = [Marketplace_offer(x) for x in search_fetch_offers(self.handler)],
            handler = self.handler,
            items = self.items
        )

    def collect_all_items(self) -> typing.List[dict]:
        """
        This function collects all items that are available to be collected.

        Returns:
        List[dict]: The list of results of the item collection.
        """
        results = []
        marketplace_offer_to_collect = self.search_sell_offer()
        for offer in marketplace_offer_to_collect:
            self.work_manager.move_to_town(offer.town_id)
            if  offer.sell_offer_completed_100_trust or offer.is_expired(self.handler):
                result = offer.fetch_offer(self.handler)
                results.append(result)
        return results
