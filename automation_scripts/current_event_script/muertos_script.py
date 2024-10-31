import typing
import random

from the_west_inner.currency import Currency
from the_west_inner.current_events.build_events import make_event_loader
from the_west_inner.current_events.current_events import CurrentEvent
from the_west_inner.requests_handler import requests_handler

from the_west_inner.current_events.muertos.muertos import MuertosEvent

def load_game_event( game_html : str , handler : requests_handler , global_currency : Currency) -> CurrentEvent | None:
    
    loader = make_event_loader(game_html = game_html)
    
    if loader is None:
        return loader
    
    event = loader.load(handler = handler,
                global_currency = global_currency
                )
    
    return event



def play_try(muertos_event : MuertosEvent , target_level : typing.Literal[1,2,3,4,5] , exception_list : list[int] ):
    
    while muertos_event.muertos_game_data.stage < target_level or muertos_event.muertos_game_data.current_prize in exception_list:
        
        if muertos_event.muertos_game_data.win():
            
            muertos_event.advance()
        
        if muertos_event.can_bet:
            
            muertos_event.start_betting()
        
        if muertos_event.muertos_game_data.can_choose_card():
            
            muertos_event.bet(random.choice([0,1,2]))
        
        if muertos_event.muertos_game_data.is_lost():
            
            muertos_event.collect()
            return
    
    if not muertos_event.muertos_game_data.win():
        
        raise Exception("You shouldn't have arrived at collecting the reward ! ")
    
    reward = muertos_event.muertos_game_data.current_prize
    
    muertos_event.collect()
    
    return reward

def muertos_script(game_html : str , 
                        handler : requests_handler , 
                        global_currency : Currency ,
                        target_level : typing.Literal[1,2,3,4,5] , 
                        exception_list : list[int]):
    event = load_game_event(
        game_html = game_html,
        handler = handler,
        global_currency = global_currency
    )
    if not isinstance(event,MuertosEvent):
        return 
    
    
    result = [play_try(muertos_event= event,
             target_level = target_level,
             exception_list= exception_list
              ) for _ in range(event.muertos_game_data.free_games) ]
    
    return [x for x in result if x is not None]