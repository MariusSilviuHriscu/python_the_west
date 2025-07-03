import requests
from connection_sessions.opera.opera_handler import OperaProxyHandler
from connection_sessions.standard_request_session import HeadersType, StandardRequestsSession


class OperaRequestsSession(StandardRequestsSession):
    def __init__(self, base_website: str = "https://www.the-west.ro"):
        self.base_website = base_website
        self.proxy_handler = OperaProxyHandler()
        self.current_proxy = self.proxy_handler.rotate()

        self.session = requests.Session()
        self.session.proxies = self.proxy_handler.get_proxy_dict()
        self.session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
        }

    def test_connection(self) -> bool:
        try:
            resp = self.session.get(self.base_website, timeout=10)
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def force_change_connection(self):
        print("Changing to next Opera proxy...")
        self.current_proxy = self.proxy_handler.rotate()
        self.session.proxies = self.proxy_handler.get_proxy_dict()

    def new_connection(self):
        while not self.test_connection():
            self.force_change_connection()

    def _post(self, url: str, data: dict | None = None, timeout: int = 50, allow_redirects: bool | None = None) -> requests.Response:
        return self.session.post(url, data=data, timeout=timeout, allow_redirects=allow_redirects or True)

    def _get(self, url: str, data: dict | None = None, timeout: int = 50, allow_redirects: bool | None = None) -> requests.Response:
        return self.session.get(url, params=data, timeout=timeout, allow_redirects=allow_redirects or True)

    def post(self, url: str, data: dict | None = None, timeout: int = 50, retry_per_connection: int = 3,
             allow_redirects: bool | None = None) -> requests.Response:
        for attempt in range(retry_per_connection):
            try:
                return self._post(url, data, timeout, allow_redirects)
            except requests.RequestException:
                print(f"[POST] Retry {attempt+1}")
        self.new_connection()
        return self.post(url, data, timeout, retry_per_connection, allow_redirects)

    def get(self, url: str, data: dict | None = None, timeout: int = 50, retry_per_connection: int = 3,
            allow_redirects: bool | None = None) -> requests.Response:
        for attempt in range(retry_per_connection):
            try:
                return self._get(url, data, timeout, allow_redirects)
            except requests.RequestException:
                print(f"[GET] Retry {attempt+1}")
        self.new_connection()
        return self.get(url, data, timeout, retry_per_connection, allow_redirects)

    @property
    def headers(self) -> HeadersType:
        return self.session.headers