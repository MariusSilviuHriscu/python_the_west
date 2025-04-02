import typing

from the_west_inner.requests_handler import requests_handler
from the_west_inner.currency import Currency

from the_west_inner.current_events.easter.build_easter_event import EasterEventBuilder
from the_west_inner.current_events.easter.easter import EasterEvent
from the_west_inner.current_events.current_event_data import EventCurrencyEnum
from the_west_inner.current_events.build_events import CurrentEventLoader,make_event_loader

def load_game_event( game_html : str , handler : requests_handler , global_currency : Currency) -> EasterEvent | None:
    
    loader = make_event_loader(game_html = game_html)
    
    event = loader.load(handler = handler,
                global_currency = global_currency
                )
    
    return event

def play_offset(event : EasterEvent , offset : typing.Literal[0,1,2,3]):
    if event.can_duel_by_offset(offset= offset , currency_type= EventCurrencyEnum.FIREWORK):
        
        item =event.duel_bandit(
            bandit_data = offset,
            currency_type=  EventCurrencyEnum.FIREWORK
        )
        print(f'Item obtained {item}')

def play_bets(offset_list : list[typing.Literal[0,1,2,3]],
              event : EasterEvent              
              ):
    
    for offset in sorted(offset_list):
        
        play_offset(
            event = event ,
            offset = offset
        )

def easter_script(game_html : str , 
                        handler : requests_handler , 
                        global_currency : Currency ,
                        offset_list : list[typing.Literal[0,1,2,3]]):
    event = load_game_event(
        game_html = game_html,
        handler = handler,
        global_currency = global_currency
    )
    if not isinstance(event,EasterEvent):
        return 
    
    play_bets(offset_list= offset_list ,
              event = event
              )