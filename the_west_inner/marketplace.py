from dataclasses import dataclass

from the_west_inner.requests_handler import requests_handler
from the_west_inner.bag import Bag
from the_west_inner.items import Items
from the_west_inner.currency import Currency
from the_west_inner.movement_manager import MovementManager
from the_west_inner.player_data import Player_data

from the_west_inner.marketplace_buy import Marketplace_buy_manager
from the_west_inner.marketplace_sell import Auction_sell_manager
from the_west_inner.marketplace_pickup_manager import MarketplacePickupManager

@dataclass
class Marketplace_managers():
    marketplace_sell_manager: Auction_sell_manager
    marketplace_buy_manager:Marketplace_buy_manager
    marketplace_pickup_manager : MarketplacePickupManager


def build_marketplace_managers(handler:requests_handler,
                                     items : Items,
                                     currency : Currency,
                                     movement_manager : MovementManager,
                                     bag : Bag,
                                     player_data : Player_data
                                     ) -> Marketplace_managers:
    
    return Marketplace_managers(
        marketplace_sell_manager= Auction_sell_manager(handler=handler,
                                                       items= items,
                                                       currency = currency,
                                                       movement_manager = movement_manager,
                                                       bag= bag,
                                                       player_data = player_data
                                                       ),
        marketplace_buy_manager = Marketplace_buy_manager(

                                                        handler= handler,
                                                        items = items,
                                                        currency = currency
                                                        ),
        marketplace_pickup_manager = MarketplacePickupManager(
                                                        handler = handler,
                                                        movement_manager = movement_manager,
                                                        items = items,
                                                        bag = bag ,
                                                        currency = currency
                                                            )
    )