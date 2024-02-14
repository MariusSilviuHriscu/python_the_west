import requests
from stem import Signal
from stem.control import Controller
import time

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
def create_tor_session():
    tor_handler = TorSessionHandler()

    while not tor_handler.is_tor_connected():
        print("Waiting for Tor to start...")
        time.sleep(5)  # Wait for 5 seconds before checking again

    # Set the proxy for the requests session
    tor_proxy = {'http': 'socks5://127.0.0.1:9150', 'https': 'socks5://127.0.0.1:9150'}
    tor_handler.session.proxies.update(tor_proxy)

    return tor_handler.session

