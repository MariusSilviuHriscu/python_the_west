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
from towns import Town,TownBuildingLevelMap

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


class AuctionFeeBuilder():
    def __init__(self,handler : requests_handler,player_data : Player_data,town : Town,sell_offer:Sell_offer_data):
        self.handler = handler
        self.player_data = player_data
        self.town = town
        self.sell_offer = sell_offer
        
    def _get_town_market_data(self) -> TownBuildingLevelMap:
        return self.town.town_level_map_data(handler = self.handler,city_building_name='market')
    def _get_min_max_price(self) -> tuple[int]:
        if self.sell_offer.auctionprice == "":
            return int(self.sell_offer.maxprice),int(self.sell_offer.maxprice)
        if self.sell_offer.maxprice == "":
            return int(self.sell_offer.auctionprice),int(self.sell_offer.auctionprice)
        
        return (
                min(
                    int(self.sell_offer.maxprice),int(self.sell_offer.auctionprice)
                    ),
                max(
                    int(self.sell_offer.maxprice),int(self.sell_offer.auctionprice)
                    )
                
                )
            
        
        
    def build(self) -> AuctionFeeCalculator:
        min_price,max_price = self._get_min_max_price()
        market_stage = self._get_town_market_data()
        return AuctionFeeCalculator (
            min_price = min_price,
            max_price = max_price,
            max_days= int(self.sell_offer.auctionlength),
            auctions= int(self.sell_offer.auctioncount),
            current_stage = market_stage.level,
            max_stage = market_stage.max_level,
            is_player_town = market_stage.town_id == self.player_data.town_id
        )
    
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
                 bag : Bag,
                 player_data : Player_data
                 ):
        """
        Initializes the auction sell manager with the given parameters.

        Args:
        handler (requests_handler): The request handler to use for sending requests.
        items (Items): The items instance.
        currency (Currency): The currency instance.
        movement_manager (MovementManager): The movement manager instance.
        player_data (Player_data) : The container of character variables
        """
        self.handler = handler
        self.items = items
        self.currency = currency
        self.movement_manager = movement_manager
        self.bag = bag
        self.player_data = player_data
    def validate_item_quantity(self,offer_data : Sell_offer_data) -> bool:
        sold_item = offer_data.item_id
        item_sold_ammount = offer_data.itemcount
        if sold_item not in self.bag :
            return False
        if self.bag[sold_item] < item_sold_ammount:
            return False
        
        return True
    def validate_money_fee_value(self,town_id : int,sell_offer : Sell_offer_data) -> bool:
        town = self.movement_manager.map.towns[town_id]
        auction_fee_calculator_builder = AuctionFeeBuilder(
            handler = self.handler,
            player_data = self.player_data,
            town = town,
            sell_offer = sell_offer
        )
        auction_fee_calculator = auction_fee_calculator_builder.build()
        return auction_fee_calculator.calculate_fee() < self.currency.total_money
        
        
    def _create_auction(self, 
                        item_id: int,
                        number_of_items: int,
                        unitary_price: int,
                        town_id: int,
                        min_price : None | int = None,
                        description: str=""
                        ) -> Sell_offer_data:
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
            auctionprice="" if min_price is None else number_of_items * min_price,
            maxprice=number_of_items * unitary_price
        )
    def commit_auction(self,
                     town_id : int|str,
                     item_id : int,
                     number_of_items : int,
                     unitary_price : int,
                     min_price : None | int = None,
                     description : str = ''
                     ):
        
        
        
        auction = self._create_auction(
            item_id=item_id,
            number_of_items=number_of_items,
            unitary_price=unitary_price,
            town_id=town_id,
            min_price = min_price,
            description = description
        )
        if not self.validate_item_quantity(offer_data=auction):
            raise InvalidAuctionException('The sell offer has been invalidated')
        if not self.validate_money_fee_value(town_id = town_id,sell_offer=auction):
            raise ValueError('Not enough money to pay the fee')
        
        result = put_product_on_market(
            handler = self.handler,
            sell_offer_data = auction
        )
        self.currency.modify_money(new_cash = result['money'],new_deposit=result['deposit'])
        self.bag.consume_item(item_id=item_id,amount=number_of_items)
        
        return result
        
    def sell_in_nearest_town(self,
                             item_id: int,
                             number_of_items: int,
                             unitary_price: int,
                             min_price : None | int = None,
                             description: str="",
                             minimise_tax_flag : bool = False
                             ) -> typing.Optional[dict]:
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
        
        if min_price is not None and minimise_tax_flag:
            raise ValueError('You both provided a minimum value and you selected the minimise tax flag ! ')
        
        if minimise_tax_flag:
            min_price : int = int (
                                    self.items.find_item(item_id=item_id).get('sell_price') 
                                )
        
        town_id = self.movement_manager.move_to_closest_town()
        
        return self.commit_auction(town_id=town_id,
                                 item_id = item_id,
                                 number_of_items= number_of_items,
                                 unitary_price = unitary_price,
                                 min_price = min_price ,
                                 description = description
                                 )