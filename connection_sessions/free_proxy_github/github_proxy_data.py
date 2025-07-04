import threading
import queue
import requests
from typing import Generator, Iterator

class GithubProxyManager:
    def __init__(self, url: str) -> None:
        self.url: str = url
        self.proxy_queue: queue.Queue[str] = queue.Queue()
        self.lock: threading.Lock = threading.Lock()
        self._refill_proxies()

    def _refill_proxies(self) -> None:
        try:
            response = requests.get(self.url)
            proxy_list: list[str] = [x for x in response.text.split('\n')]
            print(f"[ProxyManager] Fetched {len(proxy_list)} proxies from URL: {self.url}")
            for proxy in proxy_list:
                self.proxy_queue.put(proxy)
            print(f"[ProxyManager] Refilled {len(proxy_list)} proxies from URL.")
        except Exception as e:
            print(f"[ProxyManager] Failed to fetch proxy list: {e}")

    def get_ip(self) -> Generator[str, None, None]:
        def proxy_generator() -> Iterator[str]:
            while True:
                try:
                    proxy: str = self.proxy_queue.get_nowait()
                    yield proxy
                except queue.Empty:
                    with self.lock:
                        if self.proxy_queue.empty():  # Double-check
                            self._refill_proxies()
                    continue  # After refill, retry
        return proxy_generator()

