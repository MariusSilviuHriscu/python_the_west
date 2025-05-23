from dataclasses import dataclass
import requests
from urllib.parse import urlparse
import datetime
import time
from requests.exceptions import ConnectionError
#from urllib3.exceptions import ConnectionError

from requests.exceptions import ConnectionError as RequestsConnectionError
from http.client import RemoteDisconnected
from urllib3.exceptions import ProtocolError

from functools import wraps

from connection_sessions.standard_request_session import StandardRequestsSession

from the_west_inner.requests_rate_limiter import rate_limited

def requests_url_decorator(funct):
    def inner(*args,**kwargs):
        a = funct(*args,**kwargs)
        print(f"{a} at {datetime.datetime.now()}",end="\r")
        return a
    return inner

def retry_on_remote_disconnection(retries=3, delay=2):
    """
    Retry decorator for handling RemoteDisconnected errors.

    Args:
        retries (int): Number of retry attempts. Defaults to 3.
        delay (int): Delay between retry attempts in seconds. Defaults to 2.

    Returns:
        function: The wrapped function with retry logic.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < retries:
                try:
                    return func(*args, **kwargs)
                except ConnectionError as e:
                    attempts += 1
                    print(f"ConnectionError encountered. Retry attempt {attempts}/{retries} after {delay} seconds.")
                    if attempts < retries:
                        time.sleep(delay)
                    else:
                        print("Max retries reached. Raising exception.")
                        raise e
        return wrapper
    return decorator

def retry_on_remote_disconnection(retries=3, delay=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < retries:
                try:
                    return func(*args, **kwargs)
                except (RequestsConnectionError, RemoteDisconnected, ProtocolError) as e:
                    attempts += 1
                    print(f"Connection error encountered: {e}. Retry attempt {attempts}/{retries} after {delay} seconds.")
                    if attempts < retries:
                        time.sleep(delay)
                    else:
                        print("Max retries reached. Raising exception.")
                        raise e
        return wrapper
    return decorator

#@requests_url_decorator
def request_url(base_url, window, action, h=None, action_name="action"):
    """
    Construct a formatted URL for a game request.

    Args:
        base_url (str): The base URL of the game server.
        window (str): The game window or context.
        action (str): The specific action to perform in the game.
        h (str): Optional hash parameter. Defaults to None.
        action_name (str): The name of the action parameter. Defaults to "action".

    Returns:
        str: Formatted URL for the game request.
    """
    url = urlparse(base_url)._replace(query=f'window={window}&{action_name}={action}') if h is None else urlparse(
        base_url)._replace(query=f'window={window}&action={action}&h={h}')
    return url.geturl()

@retry_on_remote_disconnection(retries=30, delay=3)
def request_game(session : requests.Session | StandardRequestsSession, base_url, window, action, payload=None, h=None, action_name="action"):
    """
    Make a game request to the specified server.

    Args:
        session (requests.Session): The requests session to use.
        base_url (str): The base URL of the game server.
        window (str): The game window or context.
        action (str): The specific action to perform in the game.
        payload (dict): Optional payload data for the request. Defaults to None.
        h (str): Optional hash parameter. Defaults to None.
        action_name (str): The name of the action parameter. Defaults to "action".

    Returns:
        dict: JSON response from the game server.
    """
    if payload is not None:
        r = session.post(request_url(base_url, window, action, h, action_name=action_name), data=payload,timeout=50)
    else:
        r = session.post(request_url(base_url, window, action, h, action_name=action_name) ,timeout=50)
    return r.json()

@dataclass
class requests_handler:
    """
    Wrapper class for making game requests using the requests library.

    Attributes:
        session (requests.Session): The requests session to use.
        base_url (str): The base URL of the game server.
        h (str): The hash parameter for authentication.
    """
    session: requests.Session | StandardRequestsSession
    base_url: str
    h: str

    @rate_limited(limit=3, duration=4)
    def post(self, window, action, action_name="action", payload=None, use_h=False):
        """
        Make a POST request to the game server.

        Args:
            window (str): The game window or context.
            action (str): The specific action to perform in the game.
            action_name (str): The name of the action parameter. Defaults to "action".
            payload (dict): Optional payload data for the request. Defaults to None.
            use_h (bool): Flag to include the hash parameter. Defaults to False.

        Returns:
            dict: JSON response from the game server.
        """
        return request_game(self.session, self.base_url, window, action, payload,
                            self.h if use_h else None, action_name=action_name)
