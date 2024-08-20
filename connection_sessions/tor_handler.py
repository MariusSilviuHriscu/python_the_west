import typing
import time

import requests
from stem import Signal
from stem.control import Controller


from connection_sessions.standard_request_session import HeadersType


class TorSessionHandler:
    def __init__(self):
        self.session = requests.Session()
        self.tor_controller = None

    def is_tor_connected(self):
        try:
            self.tor_controller = Controller.from_port(port=9051)
            self.tor_controller.connect()
            return True
        except ConnectionRefusedError:
            print("Connection to Tor control port refused. Make sure Tor is running.")
            return False
        except Exception as e:
            print(f"Error connecting to Tor: {e}")
            return False
        finally:
            if self.tor_controller:
                self.tor_controller.close()

    def get_proxy_ip(self,url='https://api64.ipify.org?format=json'):
        try:
            # Make a request using the proxy-enabled session
            response = self.session.get(url)
            data = response.json()
            return data['ip']   
        except Exception as e:
            print(f"Error retrieving proxy IP: {e}")
            return None
    def renew_connection(self):
        try:
            
            with Controller.from_port(port = 9051) as controller:
                controller.authenticate('password')  # provide the password here if you set one

                
                controller.signal(Signal.NEWNYM)
                time.sleep(controller.get_newnym_wait())
                
                session = requests.Session()
                tor_proxy = {'http': 'socks5://127.0.0.1:9150', 'https': 'socks5://127.0.0.1:9150'}
                session.proxies.update(tor_proxy)
                self.session = session
                print(f'We have changes tor ip adress to {self.get_proxy_ip()}')
        except Exception as e:
            print(f"Error renewing Tor connection: {e}")
        finally:
            if self.tor_controller:
                self.tor_controller.close()

    def is_connection_fast(self, test_url='https://www.google.com', timeout=5):
        try:
            start_time = time.time()
            response = self.session.get(test_url, timeout=timeout)
            elapsed_time = time.time() - start_time
            return response.status_code == 200 and elapsed_time < timeout
        except Exception as e:
            print(f"Error checking connection speed: {e}")
            return False

class TorRequestsSession():
    def __init__(self,
                 tor_handler : TorSessionHandler , 
                 session : requests.Session ,
                 base_website : str = 'https://www.the-west.ro'):
        self.tor_handler = tor_handler
        self.session = session
        self.base_website  = base_website
                
    def test_connection(self) -> bool:
        
        try :
            response = self.session.get(self.base_website)
            return response.status_code == 200
        
        except requests.ConnectTimeout as e:
            
            return False
        except requests.ConnectionError as e:
            return False
        except requests.HTTPError as e:
            return False
        
    def force_change_connection(self):
        
        self.tor_handler.renew_connection()
        
    def new_connection(self):
        
        while not self.test_connection() :
            
            self.force_change_connection()    
    
    def _post(self,
              url : str ,
              data : dict | None = None ,
              timeout : int = 50 ,
              allow_redirects : bool | None = None) -> requests.Response:
        if allow_redirects is None:
            return self.session.post(url=url , data= data , timeout= timeout)
        return self.session.post(url=url , data= data , timeout= timeout , allow_redirects= allow_redirects)
    def _get(self,
              url : str ,
              data : dict | None = None ,
              timeout : int = 50 ,
              allow_redirects : bool | None = None) -> requests.Response:
        if allow_redirects is None:
            return self.session.post(url=url , data= data , timeout= timeout)
        return self.session.post(url=url , data= data , timeout= timeout , allow_redirects= allow_redirects)
    
    def post(self,
             url : str , 
             data : dict | None = None ,
             timeout : int = 50 ,
             retry_per_connection : int = 3 ,
             allow_redirects : bool | None = None):
        for _ in range(retry_per_connection):
            
            try :
                return self._post(url = url , 
                                  data = data ,
                                  timeout= timeout ,
                                  allow_redirects = allow_redirects)
            except:
                print(f'Tried to get url try number {_}')
        self.new_connection()
        return self.post(url=url , 
                         data=data ,
                         timeout=timeout ,
                         retry_per_connection = retry_per_connection,
                         allow_redirects = allow_redirects
                         )
    def get(self,
             url : str , 
             data : dict | None = None ,
             timeout : int = 50 ,
             retry_per_connection : int = 3 ,
             allow_redirects : bool | None = None):
        for _ in range(retry_per_connection):
            
            try :
                return self._get(url = url , 
                                  data = data ,
                                  timeout= timeout ,
                                  allow_redirects = allow_redirects)
            except:
                print(f'Tried to get url try number {_}')
        self.new_connection()
        return self.get(url=url , 
                         data=data ,
                         timeout=timeout ,
                         retry_per_connection = retry_per_connection,
                         allow_redirects = allow_redirects
                         )
    
    @property
    def headers(self) -> HeadersType:
        
        return self.session.headers

            


def create_tor_session() -> TorRequestsSession:
    tor_handler = TorSessionHandler()

    while not tor_handler.is_tor_connected():
        print("Waiting for Tor to start...")
        time.sleep(5)  # Wait for 5 seconds before checking again

    # Set the proxy for the requests session
    tor_proxy = {'http': 'socks5://127.0.0.1:9150', 'https': 'socks5://127.0.0.1:9150'}
    tor_handler.session.proxies.update(tor_proxy)
    tor_handler.session.headers = {"User-Agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}
    
    
    return TorRequestsSession(
        tor_handler = tor_handler,
        session = tor_handler.session
    )

