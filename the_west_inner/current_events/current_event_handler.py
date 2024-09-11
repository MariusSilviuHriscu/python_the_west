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
    
    def init_event(self , wof_id : int) -> dict:
        payload = {'wofid' : wof_id}
        
        response = self.handler.post(
            window = 'wheeloffortune',
            action = 'init',
            action_name = 'mode',
            payload=payload
        )
        
        return response
