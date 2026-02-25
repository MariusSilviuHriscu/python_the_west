from the_west_inner.bag import Bag
from the_west_inner.consumable import Consumable_handler
from the_west_inner.game_classes import Game_classes
from the_west_inner.requests_handler import requests_handler

EVENT_DROP_ITEMS = [
    54699000,
    50842000,
    50843000,
    50844000,
    50840000,
    51326000,
    51329000,
    51327000,
    51328000,
    51814000,
    51815000,
    51812000,
    51813000,
    54661000,
    52747000,
    52267000,
    52748000,
    52270000,
    52749000,
    52746000,
    52269000,
    54688000
]


def _open_use(bag : Bag , consumable_handler : Consumable_handler):
    
    for item_id in EVENT_DROP_ITEMS:
        
        if bag[item_id] != 0 :
            
            result = consumable_handler.open_box(
                box_id = item_id,
                number = bag[item_id]
            )
            print(result)

def open_event_use(game_classes : Game_classes , handler : requests_handler ):
    handler = game_classes.handler
    bag = game_classes.bag
    consumable_handler = game_classes.consumable_handler
    
    _open_use(bag=bag , consumable_handler= consumable_handler)
    
    bag.update_inventory(handler= handler)
    
    _open_use(bag=bag , consumable_handler= consumable_handler)
    
    