import typing

from the_west_inner.requests_handler import requests_handler
from the_west_inner.currency import Currency

from the_west_inner.current_events.build_events import make_event_loader,CurrentEventLoader
from the_west_inner.current_events.current_event_data import EventCurrencyEnum

from the_west_inner.current_events.heart.heart import HeartEvent


def load_game_event( game_html : str , handler : requests_handler , global_currency : Currency) -> HeartEvent | None:
    
    loader = make_event_loader(game_html = game_html)
    
    event = loader.load(handler = handler,
                global_currency = global_currency
                )
    
    return event

def play_offset(event : HeartEvent,currency_type : EventCurrencyEnum ):
    
    item = event.play(currency_type= currency_type)
    
    print(f'Item obtained {item}')

def play_bets(offset_list : int,
              event : HeartEvent,
              currency_type : EventCurrencyEnum           
              ):
    
    play_target_num = event.get_play_times(
        currency_type = currency_type,
        limit = offset_list
    )
    
    for _ in range(play_target_num):
        
        play_offset(
            event = event,
            currency_type = currency_type
        )

def heart_script(game_html : str , 
                        handler : requests_handler , 
                        global_currency : Currency ,
                        event_bet_offset : int):
    event = load_game_event(
        game_html = game_html,
        handler = handler,
        global_currency = global_currency
    )
    if not isinstance(event,HeartEvent):
        return 
    
    play_bets(offset_list= event_bet_offset ,
              event = event
              )