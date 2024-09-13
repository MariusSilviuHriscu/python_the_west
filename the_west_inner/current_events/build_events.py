from typing import Protocol
import typing

from the_west_inner.requests_handler import requests_handler
from the_west_inner.currency import Currency

from the_west_inner.current_events.current_events import CurrentEvent

from the_west_inner.init_data import return_current_event_data,get_wof_id_by_event_name,return_current_fair_data

from the_west_inner.current_events.independence.build_independence_event import IndependenceEventBuilder
from the_west_inner.current_events.oktoberfest.build_oktoberfest_event import OktoberfestEventBuilder


class EventBuilder(Protocol):
    handler:requests_handler
    currency : Currency
    wof_id : int 
    event_currency_ammount : int
    event_currency_name : str 
    event_name : str
    def build_event(self) -> CurrentEvent:
        pass


EVENT_DICT : dict[str, EventBuilder] ={
    'Independence' : IndependenceEventBuilder,
    'Octoberfest' : OktoberfestEventBuilder,
    'fairwof' : None
}


class CurrentEventLoader:
    def __init__(self ,
                 wof_id : int,
                 event_key : int,
                 currency_ammount : int,
                 currency_name : str
                 ):
        self.wof_id = wof_id
        self.event_key = event_key
        self.currency_ammount = currency_ammount
        self.currency_name = currency_name
    
    def load(self , handler : requests_handler , global_currency : Currency) -> CurrentEvent | None:
        
        builder_class_type = EVENT_DICT.get(self.event_key,None)
        
        if builder_class_type is None:
            return None
        
        builder : EventBuilder = builder_class_type(
            handler = handler,
            currency = global_currency,
            wof_id= self.wof_id ,
            event_currency_ammount = self.currency_ammount ,
            event_currency_name = self.currency_name,
            event_name=self.event_key
        )
        
        return builder.build_event()
def make_event_loader(game_html : str) -> CurrentEventLoader|None:
    
    current_event_list  = return_current_event_data(initialization_html = game_html)
    
    if current_event_list == []:
        return None
    
    for event_name, event_dict in current_event_list.items():
        
        if event_name in EVENT_DICT:
            
            wof_id = get_wof_id_by_event_name(initialization_html = game_html , event_name = event_name)
            
            return CurrentEventLoader(
                wof_id = wof_id,
                event_key = event_name,
                currency_ammount = event_dict.get('counter').get('value'),
                currency_name = event_dict.get('currency_id')
            )


def make_fair_event_loader(game_html : str ) -> CurrentEventLoader|None:
    
    fair_event_data = return_current_fair_data(initialization_html= game_html)
    
    if fair_event_data == {}:
        return None
    
    wof_id = get_wof_id_by_event_name(initialization_html = game_html , event_name = fair_event_data.get('name'))
    
    
    return CurrentEventLoader(wof_id = wof_id,
                              event_key= fair_event_data.get('name'),
                              currency_ammount= 0,
                              currency_name= 'free'
                              )