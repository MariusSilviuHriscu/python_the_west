
from requests_handler import requests_handler
from items import Items

from marketplace_buy import Marketplace_buy_manager
from marketplace_sell import Auction_sell_manager
class Marketplace_interface():
    def __init__(self,marketplace_sell_manager: Auction_sell_manager,marketplace_buy_manager:Marketplace_buy_manager):
        self.marketplace_sell_manager = marketplace_sell_manager
        self.marketplace_buy_manager = marketplace_buy_manager
     