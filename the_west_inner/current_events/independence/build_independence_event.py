from the_west_inner.requests_handler import requests_handler
from the_west_inner.currency import Currency

from the_west_inner.current_events.current_event_handler import EventHandler
from the_west_inner.current_events.current_event_data import CurrentEventData,EventCurrency
from the_west_inner.current_events.load_event_data import load_current_event,build_current_event_data

from the_west_inner.current_events.independence.indepencence import (
    IndependenceEvent,
    IndependenceEventData,
    IndependenceBuildingData
    )


class IndependenceEventBuilder :
    
    def __init__(self,
                 handler:requests_handler,
                 currency : Currency,
                 wof_id : int ,
                 event_currency_ammount : int,
                 event_currency_name : str ,
                 event_name : str
                 ):
        self.handler = handler
        self.currency = currency
        self.wof_id = wof_id
        self.event_name = event_name
        self.event_currency_ammount = event_currency_ammount
        self.event_currency_name = event_currency_name
    
    def make_event_handler(self ) -> EventHandler:
        
        return EventHandler(handler = self.handler)
    
    def make_event_currency(self) -> EventCurrency:
        return EventCurrency(
            currency_key = self.event_currency_name,
            currency_value= self.event_currency_ammount
        )
    
    def build_independence_event_data(self , response : dict[str , str | dict]) -> IndependenceEventData:
        return IndependenceEventData(
            buildings = [IndependenceBuildingData.build_from_dict(dict_data=x) for x in 
                                            response.get('mode').get('states').values()
                                                ]
        )
    
    def build_event(self) -> IndependenceEvent:
        
        event_handler = self.make_event_handler()
        event_currency = self.make_event_currency()
        event_response = load_current_event(event_handler = event_handler , wof_id=self.wof_id)
        
        return IndependenceEvent(
            currency = self.currency,
            event_handler = event_handler,
            current_event_data = build_current_event_data(
                response = event_response,
                event_currency_ammount = event_currency,
                wof_id = self.wof_id
            ),
            independence_event_data = self.build_independence_event_data(response=event_response)
        )