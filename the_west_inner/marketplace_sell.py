"""
This module contains functions and a class for interacting with the marketplace in a game.

Functions:

search_fetch_offers: Fetches the offers in the marketplace using a provided request handler.
put_product_on_market: Puts a product on the marketplace using a provided request handler and Sell_offer_data object.
Classes:

Sell_offer_data: Represents the data required to put a product on the marketplace.
Auction_sell_manager: A manager for auctioning and selling products on the marketplace, with methods for going to the closest town, finding the best offer for a product, buying a product, and auctioning or selling a product.
"""
import math

from requests_handler import requests_handler
from items import Items
from dataclasses import dataclass
import typing
from currency import Currency
from bag import Bag
from movement_manager import MovementManager
from player_data import Player_data
from towns import Town

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

class AuctionFeeCalculator:
    def __init__(self, min_price, max_price, max_days, auctions, current_stage,max_stage, is_player_town):
        self.min_price = min_price
        self.max_price = max_price
        self.max_days = max_days
        self.auctions = auctions
        self.current_stage = current_stage
        self.max_stage = max_stage
        self.is_player_town = is_player_town

    def calculate_fee(self) -> int:
        # Determine the effective price based on min and max prices
        effective_price = min(self.max_price, self.min_price) if self.max_price and self.min_price else max(self.max_price, self.min_price)
    
        # Calculate the temporary fee based on the effective price and other factors
        tmp_fee = int((effective_price * 0.02 * self.max_stage) + (self.max_days * 3))
    
        # Determine the final fee based on current stage and player's town status
        base_fee = tmp_fee / self.current_stage
        final_fee = math.ceil(base_fee * (1 if self.is_player_town else 2) * self.auctions)
    
        return final_fee

@dataclass
class MarketBuildingData:
    level : int
    max_level : int
class AuctionFeeBuilder():
    def __init__(self,player_data : Player_data,town : Town,sell_offer:Sell_offer_data):
        
        self.player_data = player_data
        self.town = town
        self.sell_offer = sell_offer
    
    def _get_town_market_data(self) -> MarketBuildingData:
        
        pass

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
        print(result)
        raise Exception("Could not put on market")
    return result["msg"]

class InvalidAuctionException(Exception):
    pass
class Auction_sell_manager:
    """
    This class represents a manager for auctioning and selling products on the marketplace.
    """

    def __init__(self,
                 handler: requests_handler, 
                 items: Items,
                 currency: Currency,
                 movement_manager: MovementManager,
                 bag : Bag
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
        self.bag = bag
    def validate_auction(self,offer_data : Sell_offer_data) -> bool:
        sold_item = offer_data.item_id
        item_sold_ammount = offer_data.itemcount
        if sold_item not in self.bag :
            return False
        if self.bag[sold_item] < item_sold_ammount:
            return False
        
        return True
        
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
    def sell_in_town(self,
                     town_id : int|str,
                     item_id : int,
                     number_of_items : int,
                     unitary_price : int,
                     description : str = ''
                     ):
        
        
        
        auction = self._create_auction(
            item_id=item_id,
            number_of_items=number_of_items,
            unitary_price=unitary_price,
            town_id=town_id,
            description = description
        )
        if not self.validate_auction(offer_data=auction):
            raise InvalidAuctionException('The sell offer has been invalidated')
        result = put_product_on_market(
            handler = self.handler,
            sell_offer_data = auction
        )
        self.currency.modify_money(new_cash = result['money'],new_deposit=result['deposit'])
        self.bag.consume_item(item_id=item_id,amount=number_of_items)
        
        return result
        
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
        
        return self.sell_in_town(town_id=town_id,
                                 item_id = item_id,
                                 number_of_items= number_of_items,
                                 unitary_price = unitary_price,
                                 description = description
                                 )