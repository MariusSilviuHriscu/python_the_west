

from the_west_inner.currency import Currency
from the_west_inner.current_events.current_event_handler import EventHandler
from the_west_inner.current_events.fair.fair import FairEvent, FairEventData
from the_west_inner.requests_handler import requests_handler


class FairEventBuilder :
    
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
    

    def build_fair_event_data(self ) -> FairEventData:
        return FairEventData(
            free_tries = self.event_currency_ammount
        )
    
    def build_event(self) -> FairEvent:
        
        event_handler = self.make_event_handler()
        
        return FairEvent(
            currency = self.currency,
            event_handler= event_handler,
            current_event_data = None,
            
        )