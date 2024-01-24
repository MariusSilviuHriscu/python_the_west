from datetime import datetime
from dataclasses import dataclass

from the_west_inner.login import Game_login
from the_west_inner.currency import Currency
from the_west_inner.marketplace import build_marketplace_managers,Marketplace_managers
from the_west_inner.marketplace_buy import Marketplace_buy_manager,Marketplace_offer,Marketplace_offer_list
from the_west_inner.items import Items

from the_west_inner.game_classes import Game_classes

from .marketplace_data import MarketplaceDataAnalyser

@dataclass
class MarketBuyTarget:
    item_id : int
    item_price_per_unit : int
    item_max_price : int = None

class MarketplaceProductObserver():
    
    def __init__(self ,
                 marketplace_buy_manager : Marketplace_buy_manager,
                 currency : Currency ,
                 items : Items ,
                 marketplace_data_analyser : MarketplaceDataAnalyser,
                 item_list : list[MarketBuyTarget]):
        self.marketplace_buy_manager = marketplace_buy_manager
        self.items = items
        self.currency = currency
        self.marketplace_data_analyser = marketplace_data_analyser
        self.item_list = item_list
        self.item_dict = {x.item_id : x for x in self.item_list}
    def _item_dict(self,item_id:int) -> dict:
        return self.items.get_item(item_id = item_id)
        
    def _search_for_item(self, item_target: MarketBuyTarget):
        items_offers: Marketplace_offer_list = self.marketplace_buy_manager._search_item(item_id=item_target.item_id)
        
        def filter_func(offer: Marketplace_offer) -> bool:
            if item_target.item_max_price is None:
                return offer.item_price_per_unit <= item_target.item_price_per_unit
            return offer.item_price_per_unit <= item_target.item_price_per_unit and offer.item_price < item_target.item_max_price
        
        filtered_item_offers = items_offers.filter(condition_func=filter_func)
        filtered_item_offers.buy_all(player_currency=self.currency)

        # Save all offers to the database
        self.marketplace_data_analyser.save_offers_to_database(items_offers)
    def search_item(self,item_id : int):
        self._search_for_item(item_target = self.item_dict.get(item_id))
    
    def search_all(self):
        for item_target in self.item_list:
            self._search_for_item(item_target=item_target)
    
def build_market_observer(game_data : Game_classes,item_list:list[MarketBuyTarget]) -> MarketplaceProductObserver:
    marketplace = build_marketplace_managers(
                        handler = game_data.handler,
                        items=game_data.items,
                        currency=game_data.currency,
                        movement_manager=game_data.movement_manager,
                        bag=game_data.bag,
                        player_data=game_data.player_data
                    )
    return MarketplaceProductObserver(
        marketplace_buy_manager= marketplace.marketplace_buy_manager,
        currency=game_data.currency,
        items= game_data.items,
        marketplace_data_analyser= MarketplaceDataAnalyser(database_url="sqlite:///marketplace_data.db"),
        item_list=item_list
        
    )