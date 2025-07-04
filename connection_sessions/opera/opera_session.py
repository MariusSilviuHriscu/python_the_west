import requests


class OperaRequestsSession:
    def __init__(self, base_website: str = "https://www.the-west.ro"):
        self.base_website = base_website
        self.session = requests.Session()

        self.session.proxies = {
            "http": "http://127.0.0.1:18080",
            "https": "http://127.0.0.1:18080",
        }

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

    def get(self, url: str, **kwargs):
        return self.session.get(url, **kwargs)

    def post(self, url: str, data: dict | None = None, **kwargs):
        return self.session.post(url, data=data, **kwargs)
