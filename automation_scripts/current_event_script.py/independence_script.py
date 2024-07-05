import typing

from the_west_inner.requests_handler import requests_handler
from the_west_inner.currency import Currency

from the_west_inner.current_events.independence.build_independence_event import IndependenceEventBuilder
from the_west_inner.current_events.independence.indepencence import IndependenceEvent
from the_west_inner.current_events.current_event_data import EventCurrencyEnum
from the_west_inner.current_events.build_events import CurrentEventLoader,make_event_loader

def load_game_event( game_html : str , handler : requests_handler , global_currency : Currency) -> IndependenceEventBuilder | None:
    
    loader = make_event_loader(game_html = game_html)
    
    event = loader.load(handler = handler,
                global_currency = global_currency
                )
    
    return event

def collect_available_rewards(event : IndependenceEvent) -> dict[str,int]:
    
    return event.collect_all_available()

def play_offset(event : IndependenceEvent , offset : typing.Literal[0,1,2,3]) :
    
    if event.can_build_by_offset(offset=offset , currency_type=EventCurrencyEnum.FIREWORK):
        
        event.build_by_offset(offset = offset , currency_type= EventCurrencyEnum.FIREWORK)

def play_bets(offset_list : list[typing.Literal[0,1,2,3]],
              event : IndependenceEvent              
              ):
    
    for offset in sorted(offset_list):
        
        play_offset(
            event = event ,
            offset = offset
        )

def independence_script(game_html : str , 
                        handler : requests_handler , 
                        global_currency : Currency ,
                        offset_list : list[typing.Literal[0,1,2,3]]):
    event = load_game_event(
        game_html = game_html,
        handler = handler,
        global_currency = global_currency
    )
    if event is None:
        return
    collect_available_rewards(event= event)
    
    play_bets(offset_list= offset_list ,
              event = event
              )