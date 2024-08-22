from dataclasses import dataclass
import random
from typing import Optional, Dict, Any
import typing

@dataclass
class IPData:
    as_: str
    asname: str
    city: str
    continent: str
    continentCode: str
    country: str
    countryCode: str
    district: str
    hosting: bool
    isp: str
    lat: float
    lon: float
    mobile: bool
    org: str
    proxy: bool
    regionName: str
    status: str
    timezone: str
    zip: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'IPData':
        return IPData(
            as_=data.get('as', ''),
            asname=data.get('asname', ''),
            city=data.get('city', ''),
            continent=data.get('continent', ''),
            continentCode=data.get('continentCode', ''),
            country=data.get('country', ''),
            countryCode=data.get('countryCode', ''),
            district=data.get('district', ''),
            hosting=data.get('hosting', False),
            isp=data.get('isp', ''),
            lat=data.get('lat', 0.0),
            lon=data.get('lon', 0.0),
            mobile=data.get('mobile', False),
            org=data.get('org', ''),
            proxy=data.get('proxy', False),
            regionName=data.get('regionName', ''),
            status=data.get('status', ''),
            timezone=data.get('timezone', ''),
            zip=data.get('zip', '')
        )

@dataclass
class ProxyData:
    alive: bool
    alive_since: float
    anonymity: str
    average_timeout: float
    first_seen: float
    ip_data: IPData
    ip_data_last_update: float
    last_seen: float
    port: int
    protocol: str
    proxy: str
    ssl: bool
    timeout: float
    times_alive: int
    times_dead: int
    uptime: float
    ip: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ProxyData':
        return ProxyData(
            alive=data.get('alive', False),
            alive_since=data.get('alive_since', 0.0),
            anonymity=data.get('anonymity', ''),
            average_timeout=data.get('average_timeout', 0.0),
            first_seen=data.get('first_seen', 0.0),
            ip_data=IPData.from_dict(data.get('ip_data', {})),
            ip_data_last_update=data.get('ip_data_last_update', 0.0),
            last_seen=data.get('last_seen', 0.0),
            port=data.get('port', 0),
            protocol=data.get('protocol', ''),
            proxy=data.get('proxy', ''),
            ssl=data.get('ssl', False),
            timeout=data.get('timeout', 0.0),
            times_alive=data.get('times_alive', 0),
            times_dead=data.get('times_dead', 0),
            uptime=data.get('uptime', 0.0),
            ip=data.get('ip', '')
        )
    def __hash__(self) -> int:
        
        return hash(self.proxy)

class ProxyList:
    
    def __init__(self , proxy_list : list[ProxyData]):
        self.proxy_list = proxy_list
    
    
    def get_proxy(self) -> ProxyData:
        
        return random.choice(self.proxy_list)
    
    def get_proxy_generator(self) -> typing.Generator[ProxyData , None , None ]:
        
        while True :
            
            yield self.get_proxy()