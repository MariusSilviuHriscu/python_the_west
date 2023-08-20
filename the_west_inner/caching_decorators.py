import time
from functools import wraps
import threading


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