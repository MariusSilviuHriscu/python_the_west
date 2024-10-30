import typing
from the_west_inner.requests_handler import requests_handler


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
        if 'error' in response and response.get('error'):
            raise Exception(f"You couldn't gamble ! Error message is  : {response.get('msg', '')} ")
        
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
    
    def bribe(self ,pay_id : int , wof_id : int):
        
        payload ={
            'payid': pay_id ,
            'action': 'bribe' ,
            'wofid': wof_id ,
        }
        
        response = self.handler.post(
            window = 'wheeloffortune',
            action= 'gamble',
            payload= payload ,
            use_h= True
        )
        
        if 'error' in response and response.get('error') == True:
            raise Exception(f"You couldn't bribe ! Error message is  : {response.get('msg', '')} ")
        
        return response
    def start_gamble(self , wof_id : int) -> dict:
        
        payload = {
            'action' : 'open',
            'wofid' : f'{wof_id}'
        }
        
        response = self.handler.post(
            window = 'wheeloffortune',
            action = 'gamble',
            payload = payload,
            use_h= True
        )
    
        if 'error' in response and response.get('error') == True:
            raise Exception(f"You couldn't start gambling ! Error message is  : {response.get('msg', '')} ")
        
        return response
    
    def choose_card(self, wof_id : int , card : typing.Literal[0,1,2]) -> dict:
        
        payload = {
            'card' : card,
            'action' : 'gamble',
            'wofid' : wof_id
        }
        
        
        response = self.handler.post(
            window = 'wheeloffortune',
            action = 'gamble',
            payload= payload,
            use_h= True
        )
        if 'error' in response and response.get('error'):
            raise Exception(f"You couldn't choose card ! Error message is  : {response.get('msg', '')} ")
        
        return response
    def continue_bet(self , wof_id : int) -> dict:
        
        payload = {
            'action' : 'continue',
            'wofid' : wof_id
        }
        
        response = self.handler.post(
            window = 'wheeloffortune',
            action = 'gamble',
            payload= payload,
            use_h= True
        )
        if 'error' in response and response.get('error'):
            raise Exception(f"You couldn't continue ! Error message is  : {response.get('msg', '')} ")
        
        return response
    def end_bet(self , wof_id : int) -> dict:
        
        payload = {
            'action' : 'end',
            'wofid' : wof_id
        }
        
        response = self.handler.post(
            window = 'wheeloffortune',
            action = 'gamble',
            payload= payload,
            use_h= True
        )
        if 'error' in response and response.get('error'):
            raise Exception(f"You couldn't end bet ! Error message is  : {response.get('msg', '')} ")
        
        return response
    def init_event(self , wof_id : int) -> dict:

        payload = {'wofid' : wof_id}
        
        response = self.handler.post(
            window = 'wheeloffortune',
            action = 'init',
            action_name = 'mode',
            payload=payload
        )
        
        return response
