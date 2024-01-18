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
from items import Items
from dataclasses import dataclass
import typing
from currency import Currency
from movement_manager import MovementManager


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
                 items: Items,
                 currency: Currency,
                 movement_manager: MovementManager
                 ):
        """
        Initializes the auction sell manager with the given parameters.

        Args:
        handler (requests_handler): The request handler to use for sending requests.
        items (Items): The items instance.
        currency (Currency): The currency instance.
        movement_manager (MovementManager): The movement manager instance.
        """
        self.handler = handler
        self.items = items
        self.currency = currency
        self.movement_manager = movement_manager

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
            town_id=town_id,
            item_id=item_id,
            itemcount=number_of_items,
            auctioncount="1",
            sellrights="2",
            auctionlength="7",
            description=description,
            auctionprice="",
            maxprice=number_of_items * unitary_price
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
        town_id = self.movement_manager.move_to_closest_town()
        auction = self._create_auction(
            item_id=item_id,
            number_of_items=number_of_items,
            unitary_price=unitary_price,
            town_id=town_id
        )
        return put_product_on_market(
            handler=self.handler,
            sell_offer_data=auction
        )
