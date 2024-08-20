import typing

import requests



HeadersType = typing.MutableMapping[str,str | bytes]


@typing.runtime_checkable
class StandardRequestsSession(typing.Protocol):
    
    def __init__(self) -> None:
        pass
    @property
    def headers(self) -> HeadersType:
        pass
    
    def get(self,url : str , data : dict | None = None ,timeout : int = 50 ) -> requests.Response:
        pass
    
    def post(self,url : str , data : dict | None = None ,timeout : int = 50 ) -> requests.Response:
        pass
    
    def test_connection(self) -> bool:
        pass
    
    def force_change_connection(self):
        pass
    
    def new_connection(self):
        pass