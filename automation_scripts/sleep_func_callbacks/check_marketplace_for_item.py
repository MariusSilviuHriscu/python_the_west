from the_west_inner.currency import Currency
from the_west_inner.game_classes import Game_classes
from the_west_inner.marketplace_buy import Marketplace_buy_manager
from the_west_inner.requests_handler import requests_handler
from the_west_inner.marketplace import Marketplace_managers,build_marketplace_managers

class Flag():
    def __init__(self, flag : bool = False):
        flag = flag


def check_marketplace(game_classes : Game_classes ,
                      item_id : int ,
                      max_price : int ,
                      flag : Flag,
                      instantly_buy : bool = False
                      ):
    
    marketplace_managers = build_marketplace_managers(handler = game_classes.handler,
                                          items = game_classes.items,
                                          currency= game_classes.currency,
                                          movement_manager = game_classes.movement_manager,
                                          bag=game_classes.bag,
                                          player_data= game_classes.player_data
                                          )
    
    marketplace_buy_manager = marketplace_managers.marketplace_buy_manager
    
    if flag.flag or not marketplace_buy_manager.is_on_market(item_id = item_id):
        return
    
    print(f'Found item {item_id} on marketplace !')
    
    if instantly_buy and game_classes.currency.total_money >= max_price:
    
        marketplace_buy_manager.buy_cheapest_marketplace_item(item_id = item_id ,
                                                          max_price= max_price
                                                          )
        
        flag.flag = True