from the_west_inner.currency import Currency
from the_west_inner.current_events.build_events import make_event_loader
from the_west_inner.current_events.current_events import CurrentEvent
from the_west_inner.requests_handler import requests_handler

def load_game_event( game_html : str , handler : requests_handler , global_currency : Currency) -> CurrentEvent | None:
    
    loader = make_event_loader(game_html = game_html)
    
    if loader is None:
        return loader
    
    event = loader.load(handler = handler,
                global_currency = global_currency
                )
    
    return event


def play_offset()