from typing import Protocol
from the_west_inner.requests_handler import requests_handler

class EventCurrency:
    
    def __init__(self , currency_key : str , currency_value : int = 0):
        self.currency_key = currency_key
        self._currency_value = currency_value
    
    @property
    def currency_value(self) -> int:
        return self._currency_value
    
    def add_currency(self , value : int ) -> None:
        
        if value + self._currency_value < 0:
            raise ValueError('Could not substract from value ')
        
        self._currency_value += value
    
    def set_value(self, value : int ) -> None:
        
        if value < 0:
            raise ValueError(f'Cannot have less than 0 {self.currency_key}')
    
    
class EventHandler():
    
    def __init__(self , handler : requests_handler):
        self.handler = handler
    
    def gamble(self,pay_id : int , gamble_level : int , wof_id):
        
        payload = {
            'payid' : pay_id,
            'enhance' : gamble_level,
            'action' : 'main',
            'wofid' : wof_id
        }
        
        
        response = self.handler.post(
            window = 'wheeloffortune',
            action = 'gamble',
            payload= payload,
            use_h= True
        )
        
        return response
    def collect(self, gamble_level : int ,wof_id:int):
        payload = {
            'enhance' : gamble_level,
            'action' : 'collect',
            'wofid' : wof_id
        }
        
        
        response = self.handler.post(
            window = 'wheeloffortune',
            action = 'gamble',
            payload= payload,
            use_h= True
        )
        
        return response
    
    def init_event(self , wof_id : int):
        payload = {'wofid' : wof_id}
        
        response = self.handler.post(
            window = 'wheeloffortune',
            action = 'init',
            action_name = 'mode',
            payload=payload
        )
        
        return response

class CurrentEventData():
    
    
    def __init__(self , 
                 event_name : str ,
                 event_currency : EventCurrency,
                 event_wof : int     
    ):
        self.event_name = event_name
        self.event_currency = event_currency
        self.event_wof = event_wof
    