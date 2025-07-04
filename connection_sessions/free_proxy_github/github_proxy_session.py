import requests
import typing
from connection_sessions.standard_request_session import HeadersType
from connection_sessions.free_proxy_github.github_proxy_data import GithubProxyManager

class GithubProxySession:
    
    def __init__(self , 
                 proxy_generator : typing.Generator[str, None, None],
                 session : requests.Session ,
                 base_website : str = 'https://www.the-west.ro') -> None:
        self.session = session
        self.base_website = base_website
        self._current_proxy = None
        self.proxy_generator = proxy_generator
        
        self.set_proxy_session()
    
    @property
    def current_proxy(self) -> str:
        
        if self._current_proxy is None:
            
            self._current_proxy = next(self.proxy_generator)
        
        return self._current_proxy
    
    def set_proxy_session(self):
        
        self.session.proxies = {
            'http': f'http://{self.current_proxy}',
            'https': f'http://{self.current_proxy}',
        }
        
        print(f'Set proxy session to {self.current_proxy}')
    
    def test_connection(self) -> bool:
        
        try :
            response = self.session.get(self.base_website,
                                        timeout= 50
                                        )
            return response.status_code == 200
        
        except requests.ConnectTimeout as e:
            
            return False
        except requests.ConnectionError as e:
            return False
        except requests.HTTPError as e:
            return False
        except requests.ReadTimeout as e:
            return False
    
    def force_change_connection(self):
        
        self._current_proxy = next(self.proxy_generator)
        print(self._current_proxy)
        self.set_proxy_session()
    
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
            return self.session.get(url=url , data= data , timeout= timeout)
        return self.session.get(url=url , data= data , timeout= timeout , allow_redirects= allow_redirects)
    
    def post(self,
             url : str , 
             data : dict | None = None ,
             timeout : int = 50,
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


class GithubProxySessionLoader:
    
    def __init__(self
                 ):
        
        self.proxy_manager = GithubProxyManager('https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt')
        
        self.proxy_generator = self.proxy_manager.get_ip()
    
    def load_session(self) -> GithubProxySession:
        session = requests.Session()
        session.headers = {"User-Agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}
        
        
        return GithubProxySession(proxy_generator=self.proxy_generator,
                                  session=session)