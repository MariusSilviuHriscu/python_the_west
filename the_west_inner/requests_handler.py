from dataclasses import dataclass
import requests
from urllib.parse import urlparse
import datetime

def requests_url_decorator(funct):
    def inner(*args,**kwargs):
        a = funct(*args,**kwargs)
        print(f"{a} at {datetime.datetime.now()}",end="\r")
        return a
    return inner
#@requests_url_decorator
def request_url(base_url, window,action,h = None,action_name = "action"):
    url = urlparse(base_url)._replace(query=f'window={window}&{action_name}={action}') if h is None else urlparse(base_url)._replace(query=f'window={window}&action={action}&h={h}')
    #print(url.geturl())
    return url.geturl()
def request_game(session,base_url, window, action,payload = None, h = None,action_name = "action"):
    if payload != None:
        r = session.post(request_url(base_url, window, action,h,action_name=action_name), data=payload)
    else:
        r = session.post(request_url(base_url, window, action,h,action_name=action_name))
    return r.json()

@dataclass
class requests_handler:
    session:requests.Session
    base_url:str
    h:str
    def post(self,window,action,action_name="action",payload = None,use_h = False):
        return request_game(self.session,self.base_url,window,action,payload,self.h if use_h else None,action_name=action_name)