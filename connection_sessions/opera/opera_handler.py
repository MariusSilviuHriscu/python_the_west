import subprocess
import csv
import json
import os
from typing import List, Dict, Optional

class OperaProxyHandler:
    def __init__(self):
        self.proxy_list: List[Dict[str, str]] = []
        self.current_proxy: Optional[Dict[str, str]] = None
        self.proxy_index: int = 0
        self.login: Optional[str] = None
        self.password: Optional[str] = None
        self.refresh_proxy_list()

    def refresh_proxy_list(self):
        print("Fetching proxy list from opera-proxy...")
        try:
            result = subprocess.run(
                ["opera-proxy.exe", "-list-proxies"],
                capture_output=True, text=True, check=True
            )
            output = result.stdout.strip().splitlines()
            csv_data = output[-(len(output)-output.index("host,ip_address,port")):]  # CSV from stdout
            reader = csv.DictReader(csv_data)
            self.proxy_list = list(reader)

            self.login = self.extract_value(output, "Proxy login:")
            self.password = self.extract_value(output, "Proxy password:")
            if self.proxy_list:
                print(f"Loaded {len(self.proxy_list)} proxies.")
            else:
                print("No proxies loaded.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to fetch proxy list: {e}")
            self.proxy_list = []

    def extract_value(self, lines: List[str], startswith: str) -> Optional[str]:
        for line in lines:
            if line.startswith(startswith):
                return line.split(startswith)[-1].strip()
        return None

    def rotate(self) -> Optional[Dict[str, str]]:
        if not self.proxy_list:
            self.refresh_proxy_list()
        if not self.proxy_list:
            return None

        self.current_proxy = self.proxy_list[self.proxy_index % len(self.proxy_list)]
        print(f"Switched to proxy: {self.current_proxy['ip_address']}:{self.current_proxy['port']}")
        self.proxy_index += 1
        return self.current_proxy

    def get_proxy_dict(self) -> Dict[str, str]:
        if not self.current_proxy:
            self.rotate()
        if not self.current_proxy or not (self.login and self.password):
            return {}

        proxy_auth = f"{self.login}:{self.password}"
        proxy_base = f"{self.current_proxy['ip_address']}:{self.current_proxy['port']}"
        proxy_url = f"https://{proxy_auth}@{proxy_base}"

        return {
            "http": proxy_url,
            "https": proxy_url,
        }

    def get_proxy_auth_header(self) -> Dict[str, str]:
        if not (self.login and self.password):
            return {}
        auth_value = f"{self.login}:{self.password}"
        encoded = auth_value.encode("utf-8")
        import base64
        return {
            "Proxy-Authorization": f"Basic {base64.b64encode(encoded).decode('utf-8')}"
        }
