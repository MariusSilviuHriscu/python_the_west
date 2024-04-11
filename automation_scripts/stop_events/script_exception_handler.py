import inspect
from functools import wraps

from automation_scripts.stop_events.script_events import RestartEventException,StopEventException

def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        instance = args[0]  # Assuming the instance is passed as the first argument
        try:
            return func(*args, **kwargs)
        except RestartEventException:
            # Restart execution from the start
            return func.__get__(instance)(*args[1:], **kwargs)
        except StopEventException:
            # Stop execution
            pass
    return wrapper

def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if inspect.ismethod(func) or (args and inspect.isclass(args[0])):
            # Check if it's a method or a function bound to an instance
            instance = args[0]
            try:
                return func(*args, **kwargs)
            except RestartEventException:
                # Restart execution from the start
                return func.__get__(instance)(*args[1:], **kwargs)
            except StopEventException:
                # Stop execution
                pass
        else:
            try:
                return func(*args, **kwargs)
            except RestartEventException:
                # Restart execution from the start
                return func(*args, **kwargs)
            except StopEventException:
                # Stop execution
                pass
    return wrapper