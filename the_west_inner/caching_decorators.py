import time
from functools import wraps
import threading

import typing


def cache_function_results(seconds):
    cache = {}
    lock = threading.Lock()
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = str(func)
            with lock:
                if key in cache:
                    value, expiry_time = cache[key]
                    if time.time() < expiry_time:
                        return value
                    else:
                        del cache[key]

                result = func(*args, **kwargs)
                cache[key] = (result, time.time() + seconds)
                return result

        return wrapper

    return decorator

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.4f} seconds to execute.")
        return result

    return wrapper


def retry_on_exception(delay: int, repeat: int, exceptions: typing.Union[type, typing.Tuple[type, ...]]):
    """
    Decorator that retries the decorated function if it raises the specified exceptions.

    Args:
        delay (int): The delay in seconds between retries.
        repeat (int): The number of retries if the exception occurs.
        exceptions (Union[type, Tuple[type, ...]]): The exception class or tuple of exception classes to catch and retry.

    Returns:
        Callable: The decorated function with retry logic.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts <= repeat:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts <= repeat:
                        print(f"Exception encountered: {e}. Retrying in {delay} seconds... (Attempt {attempts}/{repeat})")
                        time.sleep(delay)
                    else:
                        print(f"Max retries reached for function {func.__name__}.")
                        raise
        return wrapper
    return decorator