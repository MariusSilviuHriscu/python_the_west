

from the_west_inner.currency import Currency
from the_west_inner.current_events.current_event_handler import EventHandler
from the_west_inner.current_events.current_events import CurrentEvent
from the_west_inner.current_events.current_event_data import CurrentEventData


class FairEventData:
    
    def  __init__(self, free_tries : int):
        self.free_tries = free_tries



class FairEvent(CurrentEvent):
    
    def __init__(self , 
                 currency : Currency ,
                 event_handler : EventHandler , 
                 fair_event_data : FairEventData
                 ):
        
        self.currency = currency
        self.event_handler = event_handler
        self.fair_event_data = fair_event_data
    
    @property
    def free_tries(self) -> int:
        
        return self.fair_event_data.free_tries