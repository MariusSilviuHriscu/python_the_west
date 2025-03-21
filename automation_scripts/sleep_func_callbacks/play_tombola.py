from the_west_inner.requests_handler import requests_handler


def try_play_tombola(handler : requests_handler):
    data = handler.post(
        window='wheeloffortune',
        action='init',
        action_name='mode',
        payload= {
            'wofid': '1'
        }
    )
    
    if data.get('error',False):
        
        return
    
    free_plays = data.get('mode').get('free')
    if free_plays == 0:
        return
    for _ in range(free_plays):
        payload = {
            'payid' :  1 ,
            'cardid' :  4 ,
            'gametype' :  'wheel_of_fortune' ,
            'action' :  'main' ,
            'wofid' :  1
        }
        handler.post(
            window='wheeloffortune',
            action='gamble',
            payload=payload,
            use_h= True
        )