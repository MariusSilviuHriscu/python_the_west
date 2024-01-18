from dataclasses import dataclass

from requests_handler import requests_handler
from bag import Bag
from items import Items
from currency import Currency
from movement_manager import MovementManager


from marketplace_buy import Marketplace_buy_manager
from marketplace_sell import Auction_sell_manager
from marketplace_pickup_manager import MarketplacePickupManager

@dataclass
class Marketplace_managers():
    marketplace_sell_manager: Auction_sell_manager
    marketplace_buy_manager:Marketplace_buy_manager
    marketplace_pickup_manager : MarketplacePickupManager


def build_marketplace_managers(handler:requests_handler,
                                     items : Items,
                                     currency : Currency,
                                     movement_manager : MovementManager,
                                     bag : Bag
                                     ) -> Marketplace_managers:
    
    return Marketplace_managers(
        marketplace_sell_manager= Auction_sell_manager(handler=handler,
                                                       items= items,
                                                       currency = currency,
                                                       movement_manager = movement_manager
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