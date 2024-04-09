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