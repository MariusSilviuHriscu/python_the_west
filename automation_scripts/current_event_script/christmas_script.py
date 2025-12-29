import typing

from the_west_inner.game_classes import Game_classes
from the_west_inner.requests_handler import requests_handler
from the_west_inner.traveling_merchant import Travelling_merchant_manager

def christmas_open_bags(game_classes : Game_classes , item_id: int):
    if game_classes.bag[item_id] == 0:
        return
    result = game_classes.consumable_handler.open_box(
        box_id = item_id,
        number = game_classes.bag[item_id]
    )
    
    for result_id , num in result.items():
        name = game_classes.items.find_item(item_id=result_id).get('name')
        print(f'We got {name} : {num}')
    
def christmas_script( 
                        handler : requests_handler , 
                        game_classes : Game_classes ,
                        event_bet_offset : int):
    
    
    game_classes.currency.update_raw_oup(handler= handler)
    
    
    
    manager = Travelling_merchant_manager(
    handler= game_classes.handler,
    bag= game_classes.bag,
    items= game_classes.items,
    currency= game_classes.currency
    )
    if not manager.item_is_available(event_bet_offset):
        raise Exception('The desired item is not available')
    
    offer_list = manager.travelling_merchant_search_manager.load_data()
    offer = offer_list.get_by_item_id(item_id = event_bet_offset)
    
    price = offer.price_bonds
    
    buy_number = game_classes.currency.oup // price
    
    print(f'We are buying {buy_number} items')
    
    for _ in range(buy_number):
        
        manager.buy_non_trader_item(item_id = event_bet_offset)
    
    game_classes.bag.update_inventory(handler= handler)
    christmas_open_bags(
        game_classes = game_classes,
        item_id= event_bet_offset
    )