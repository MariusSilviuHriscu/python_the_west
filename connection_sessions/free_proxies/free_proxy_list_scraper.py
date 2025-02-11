from dataclasses import dataclass
import enum
import json
import typing

import requests
from json.decoder import JSONDecodeError

from connection_sessions.free_proxies.proxy_data import ProxyList,ProxyData

T = typing.TypeVar('T')
SingleOrIterableOrNone = typing.Union[T, typing.Iterable[T], None]


class FreeProxyResultFormatEnum(enum.Enum):
    
    TEXT = 'text'
    JSON = 'json'
    CSV = 'csv'

class FreeProxyFormatEnum(enum.Enum):
    
    PROTOCOL_IP_PORT = 'protocolipport'
    IP_PORT = 'ipport'

class FreeProxyAnonymityEnum(enum.Enum):
    
    ELITE = 'Elite'
    ANONYMOUS = 'Anonymous'
    TRANSPARENT = 'Transparent'

class FreeProxyProtocolEnum(enum.Enum):
    
    HTTP = 'http'
    SOCKS4 = 'socks4'
    SOCKS5 = 'socks5'


DISPLAY_REQUEST = 'displayproxies'


class FreeProxyRequest:
    default_url = 'https://api.proxyscrape.com/v3/free-proxy-list/get?'
    def __init__(self ,
                 country : SingleOrIterableOrNone[str] = None,
                 proxy_format : SingleOrIterableOrNone[FreeProxyFormatEnum] = None ,
                 protocol : SingleOrIterableOrNone[FreeProxyProtocolEnum] = None,
                 anonymity : SingleOrIterableOrNone[FreeProxyAnonymityEnum] = None,
                 format : SingleOrIterableOrNone[FreeProxyResultFormatEnum] = None,
                 timeout : int | None = None,
                 request : str = DISPLAY_REQUEST
                 ):
        
        self.country = country
        self.proxy_format = proxy_format
        self.protocol = protocol
        self.anonymity = anonymity
        self.format = format
        self.timeout = timeout
        self.request = request
    
    def _add_argument(self,argument_name : str ) -> str:
        
        to_string = lambda x : str(x.value if isinstance(x, enum.Enum) else x) 
        
        arg_value = getattr(self, argument_name)
        
        if arg_value is None:
            return ''
        
        if isinstance(arg_value, str) or isinstance(arg_value , int):
            
            return f'&{argument_name}=' + str(arg_value)
        
        if isinstance(arg_value, typing.Iterable) :
            
            return f'&{argument_name}=' + ','.join(to_string(x=x) for x in arg_value)
        
        if isinstance(arg_value , enum.Enum):
            
            return f'&{argument_name}=' + to_string(arg_value)
        
        raise ValueError(f'Unexpected value ! : {arg_value}')
    
    def create_url(self) -> str:
        
        url = ''
        
        url += self.default_url
        
        url += self._add_argument(argument_name = 'request')[1::]
        
        url += self._add_argument(argument_name = 'country')
        
        url += self._add_argument(argument_name= 'protocol')
        
        url += self._add_argument(argument_name = 'proxy_format')
        
        url += self._add_argument(argument_name = 'format')
        
        url += self._add_argument(argument_name = 'anonymity')
        
        url += self._add_argument(argument_name = 'timeout')
        
        return url
    
    def send(self ) -> requests.Response:
        
        return requests.get(self.create_url())


@dataclass
class PlayerCacheInfo:
    
    player_name : str
    proxy_data : ProxyData

PlayerCacheType = dict[ProxyData , PlayerCacheInfo]

class FreeProxyManager:
    
    def __init__(self,
                 proxy_request : FreeProxyRequest,
                 player_cache : PlayerCacheType,
                 player_name : str
                 ):
        
        self.proxy_request = proxy_request
        self.current_player_name = player_name
        self.player_cache = player_cache
        
    def get_proxy_list(self ) -> ProxyList :
        
        ip_data_result = self.proxy_request.send().text
        
        data = json.loads(ip_data_result)
        
        
        return ProxyList(
            proxy_list = [ProxyData.from_dict(data = x) for x in data.get('proxies')]
        )
    
    
    def _check_proxy(self , proxy : ProxyData):
        
        if proxy in self.player_cache and self.player_cache[proxy] != self.current_player_name:
            return False
        
        return True
        
    
    def _select_unused(self,proxy_list_generator : typing.Generator[ProxyData,None ,None] ) -> ProxyData:
        
        for proxy in proxy_list_generator:
            
            if self._check_proxy(proxy= proxy):
                return proxy
        
        
    def get_ip(self) -> typing.Generator[ProxyData,None,None]:
        
        while True :
            while True:
                try:
                    proxy_list = self.get_proxy_list()
                    break
                except JSONDecodeError:
                    continue
            
            selected_proxy = self._select_unused(proxy_list_generator = proxy_list.get_proxy_generator())
            
            self.player_cache[selected_proxy] = PlayerCacheInfo(player_name  = self.current_player_name , proxy_data= selected_proxy)
            
            yield selected_proxy
        
        