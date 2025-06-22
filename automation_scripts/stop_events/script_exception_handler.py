import inspect
from functools import wraps

from automation_scripts.stop_events.script_events import (RestartEventException,
                                                          StopEventException,
                                                          NestedStopEvent,
                                                          CompleteStopEventException
                                                          )

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
            except NestedStopEvent:
                raise StopEventException()
            except CompleteStopEventException as e:
                
                stack = inspect.stack()
                function_name = stack[0].function
                
                # Get a list of all functions in the current stack
                function_stack = [frame.function for frame in stack]
                
                first_occurrence = function_stack.index(function_name)
                if first_occurrence == 0:
                    pass
                else:
                    raise e
        else:
            try:
                return func(*args, **kwargs)
            except RestartEventException:
                # Restart execution from the start
                return func(*args, **kwargs)
            except StopEventException:
                # Stop execution
                pass
            except NestedStopEvent:
                raise StopEventException()
            except CompleteStopEventException as e:
                
                stack = inspect.stack()
                function_name = stack[0].function
                
                # Get a list of all functions in the current stack
                function_stack = [frame.function for frame in stack]
                
                first_occurrence = function_stack.index(function_name)
                if first_occurrence == 0 :
                    pass
                else:
                    raise e
            
    return wrapper



import inspect
import threading
from functools import wraps

from automation_scripts.stop_events.script_events import (
    RestartEventException,
    StopEventException,
    NestedStopEvent,
    CompleteStopEventException
)

# Thread-local storage to track decorated method call depth
_local = threading.local()

def _get_call_depth():
    """Get current call depth for decorated methods"""
    if not hasattr(_local, 'call_depth'):
        _local.call_depth = 0
    return _local.call_depth

def _increment_call_depth():
    """Increment call depth when entering a decorated method"""
    if not hasattr(_local, 'call_depth'):
        _local.call_depth = 0
    _local.call_depth += 1

def _decrement_call_depth():
    """Decrement call depth when exiting a decorated method"""
    if hasattr(_local, 'call_depth'):
        _local.call_depth = max(0, _local.call_depth - 1)

def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Track that we're entering a decorated method
        _increment_call_depth()
        current_depth = _get_call_depth()
        
        try:
            return func(*args, **kwargs)
        except RestartEventException:
            # Restart execution from the start
            try:
                if args and hasattr(args[0], func.__name__):
                    # It's a method call - get the bound method and call it
                    instance = args[0]
                    method = getattr(instance, func.__name__)
                    return method(*args[1:], **kwargs)
                else:
                    # It's a regular function call
                    return func(*args, **kwargs)
            except Exception as restart_error:
                # If restart fails, decrement depth and re-raise
                _decrement_call_depth()
                raise restart_error
        except StopEventException:
            # Stop execution gracefully
            return None
        except NestedStopEvent:
            # Convert nested stop to regular stop
            raise StopEventException()
        except CompleteStopEventException as e:
            # Handle complete stop only at the outermost decorated method (depth 1)
            if current_depth == 1:
                # We're at the outermost decorated method, handle the exception
                return None
            else:
                # We're in a nested decorated method, re-raise to bubble up
                raise e
        finally:
            # Always decrement depth when exiting
            _decrement_call_depth()
    
    return wrapper

# Alternative approach using a call stack tracker
_call_stack = threading.local()

def handle_exceptions_v2(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Initialize call stack if needed
        if not hasattr(_call_stack, 'methods'):
            _call_stack.methods = []
        
        # Add current method to the stack
        method_id = id(func)
        _call_stack.methods.append(method_id)
        is_outermost = len(_call_stack.methods) == 1
        
        try:
            return func(*args, **kwargs)
        except RestartEventException:
            # Restart execution from the start
            if args and hasattr(args[0], func.__name__):
                instance = args[0]
                method = getattr(instance, func.__name__)
                return method(*args[1:], **kwargs)
            else:
                return func(*args, **kwargs)
        except StopEventException:
            return None
        except NestedStopEvent:
            raise StopEventException()
        except CompleteStopEventException as e:
            # Handle complete stop only at the outermost decorated method
            if is_outermost:
                return None
            else:
                raise e
        finally:
            # Remove current method from the stack
            if _call_stack.methods and _call_stack.methods[-1] == method_id:
                _call_stack.methods.pop()
    
    return wrapper

# Debug version that prints what's happening
def handle_exceptions_debug(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        _increment_call_depth()
        current_depth = _get_call_depth()
        
        print(f"[DEBUG] Entering {func.__name__}, depth: {current_depth}")
        
        try:
            result = func(*args, **kwargs)
            print(f"[DEBUG] {func.__name__} completed normally")
            return result
        except RestartEventException:
            print(f"[DEBUG] RestartEventException in {func.__name__}")
            if args and hasattr(args[0], func.__name__):
                instance = args[0]
                method = getattr(instance, func.__name__)
                return method(*args[1:], **kwargs)
            else:
                return func(*args, **kwargs)
        except StopEventException:
            print(f"[DEBUG] StopEventException in {func.__name__}")
            return None
        except NestedStopEvent:
            print(f"[DEBUG] NestedStopEvent in {func.__name__}, converting to StopEventException")
            raise StopEventException()
        except CompleteStopEventException as e:
            print(f"[DEBUG] CompleteStopEventException in {func.__name__}, depth: {current_depth}")
            if current_depth == 1:
                print(f"[DEBUG] Handling CompleteStopEventException at outermost level in {func.__name__}")
                return None
            else:
                print(f"[DEBUG] Bubbling CompleteStopEventException up from {func.__name__}")
                raise e
        finally:
            print(f"[DEBUG] Exiting {func.__name__}, depth before decrement: {current_depth}")
            _decrement_call_depth()
    
    return wrapper