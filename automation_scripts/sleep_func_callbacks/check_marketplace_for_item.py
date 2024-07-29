from the_west_inner.currency import Currency
from the_west_inner.marketplace_buy import Marketplace_buy_manager


class Flag():
    def __init__(self, flag : bool = False):
        flag = flag


def check_marketplace(currency : Currency,
                      marketplace_buy_manager : Marketplace_buy_manager ,
                      item_id : int ,
                      max_price : int ,
                      flag : Flag,
                      instantly_buy : bool = False
                      ):
    
    if flag.flag or not marketplace_buy_manager.is_on_market(item_id = item_id):
        return
    
    print(f'Found item {item_id} on marketplace !')
    
    if instantly_buy and currency.total_money >= max_price:
    
        marketplace_buy_manager.buy_cheapest_marketplace_item(item_id = item_id ,
                                                          max_price= max_price
                                                          )
        
        flag.flag = True