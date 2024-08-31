


import typing
from the_west_inner.bag import Bag
from the_west_inner.consumable import Consumable_handler
from the_west_inner.items import Items
from the_west_inner.player_data import Player_data
from the_west_inner.requests_handler import requests_handler

from automation_scripts.stop_events.script_events import StopEvent

def select_usable(usable_list : list[int],bag : Bag ,stop_event_callable : None |typing.Callable[[],None] = None) -> int:
    
    stop = StopEvent(callback_func=stop_event_callable)
    
    for usable in usable_list:
        
        if bag[usable] > 0 :
            return usable
    
    stop.raise_exception()

def recharge_health(usable_list : list[int],bag : Bag ,consumable_manager : Consumable_handler,stop_event_callable : None |typing.Callable[[],None] = None):
    
    usable = select_usable(usable_list=usable_list , bag= bag , stop_event_callable= stop_event_callable)
    
    consumable_manager.use_consumable(consumable_id = usable)

def recharge_health_script(player_data : Player_data ,
                    usable_list : list[int],
                    min_percent_hp : int ,
                    bag : Bag ,
                    handler : requests_handler ,
                    consumable_manager : Consumable_handler,
                    stop_event_callable : None |typing.Callable[[],None] = None
                    ):
    
    player_data.update_all(handler= handler)
    
    if player_data.hp / player_data.hp_max * 100 > min_percent_hp:
        
        return 
    
    recharge_health(
        usable_list= usable_list ,
        bag= bag,
        consumable_manager= consumable_manager,
        stop_event_callable= stop_event_callable
    )
    
    