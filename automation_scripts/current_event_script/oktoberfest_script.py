
import typing

from the_west_inner.current_events.current_event_data import EventCurrencyEnum
from the_west_inner.current_events.current_events import CurrentEvent
from the_west_inner.current_events.oktoberfest.build_oktoberfest_event import OktoberfestEventBuilder
from the_west_inner.current_events.oktoberfest.oktoberfest import OktoberfestEvent

from the_west_inner.requests_handler import requests_handler
from the_west_inner.currency import Currency

from the_west_inner.current_events.build_events import make_event_loader

def load_game_event( game_html : str , handler : requests_handler , global_currency : Currency) -> CurrentEvent | None:
    
    loader = make_event_loader(game_html = game_html)
    
    if loader is None:
        return loader
    
    event = loader.load(handler = handler,
                global_currency = global_currency
                )
    
    return event


def play_offset(event : OktoberfestEvent , offset : typing.Literal[0,1,2,3]):
    
    if event.can_build_by_offset(offset= offset , currency_type= EventCurrencyEnum.FIREWORK):
        
        event.bid_by_offset(
            offset= offset,
            currency_type=  EventCurrencyEnum.FIREWORK
        )

def play_bets(offset_list : list[typing.Literal[0,1,2,3]],
              event : OktoberfestEvent              
              ):
    
    for offset in sorted(offset_list):
        
        play_offset(
            event = event ,
            offset = offset
        )

def oktoberfest_script(game_html : str , 
                        handler : requests_handler , 
                        global_currency : Currency ,
                        event_bet_offset : list[typing.Literal[0,1,2,3]]):
    event = load_game_event(
        game_html = game_html,
        handler = handler,
        global_currency = global_currency
    )
    if not isinstance(event,OktoberfestEvent):
        return 
    
    play_bets(offset_list= event_bet_offset ,
              event = event
              )