from the_west_inner.requests_handler import requests_handler


def try_play_tombola(handler : requests_handler):
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