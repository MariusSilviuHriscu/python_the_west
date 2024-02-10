import time
from functools import wraps

# Define the rate_limited decorator
def rate_limited(limit: int, duration: int):
    def decorator(func):
        timestamps = {}

        @wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            key = func.__name__

            if key not in timestamps:
                timestamps[key] = [current_time]
            else:
                timestamps[key] = [t for t in timestamps[key] if current_time - t <= duration]
                timestamps[key].append(current_time)

            if len(timestamps[key]) > limit:
                remaining_time = duration - (current_time - timestamps[key][0])
                sleep_time = max(0, remaining_time)
                time.sleep(sleep_time)

            return func(*args, **kwargs)

        return wrapper

    return decorator