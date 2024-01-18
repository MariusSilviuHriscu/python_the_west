from dataclasses import dataclass


from marketplace_buy import Marketplace_buy_manager
from marketplace_sell import Auction_sell_manager
from marketplace_pickup_manager import MarketplacePickupManager

@dataclass
class Marketplace_manager():
    marketplace_sell_manager: Auction_sell_manager
    marketplace_buy_manager:Marketplace_buy_manager
    marketplace_pickup_manager : MarketplacePickupManager