import subprocess
import time
import json

PROXY_LIST_REFRESH_INTERVAL = 60 * 10  # seconds


class OperaProxyHandler:
    def __init__(self, port: int = 18080):
        self.port = port
        self.proxy_list: list[dict] = []
        self.proxy_index = 0
        self.process: subprocess.Popen | None = None
        self.last_fetch_time = 0
        self.fetch_proxy_list()

    def fetch_proxy_list(self):
        now = time.time()
        if self.proxy_list and (now - self.last_fetch_time) < PROXY_LIST_REFRESH_INTERVAL:
            return

        try:
            print("Fetching proxy list from opera-proxy...")
            result = subprocess.run(
                ["opera-proxy.exe", "-list-proxies", "-json"],
                capture_output=True,
                text=True,
                check=True
            )
            self.proxy_list = json.loads(result.stdout)
            self.proxy_index = 0
            self.last_fetch_time = now
        except Exception as e:
            print(f"Failed to fetch proxy list: {e}")
            self.proxy_list = []

    def get_next_proxy(self) -> dict | None:
        self.fetch_proxy_list()
        if not self.proxy_list:
            print("No proxies available.")
            return None
        proxy = self.proxy_list[self.proxy_index]
        self.proxy_index = (self.proxy_index + 1) % len(self.proxy_list)
        return proxy

    def start_proxy(self, proxy: dict):
        self.stop_proxy()

        host = proxy["host"]
        port = proxy["port"]
        username = proxy.get("username")
        password = proxy.get("password")

        print(f"Starting opera-proxy with: {host}:{port}")

        # Build the command
        cmd = [
            "opera-proxy.exe",
            "-proxy",
            f"{username}:{password}@{host}:{port}"
        ]

        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(5)  # wait for the proxy to be ready

    def stop_proxy(self):
        if self.process:
            print("Stopping current proxy process...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.process = None

    def rotate(self):
        proxy = self.get_next_proxy()
        if proxy:
            self.start_proxy(proxy)
        return proxy

    def get_proxy_dict(self) -> dict:
        return {
            'http': f"http://127.0.0.1:{self.port}",
            'https': f"http://127.0.0.1:{self.port}",
        }

    def __del__(self):
        self.stop_proxy()