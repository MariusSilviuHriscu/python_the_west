import typing
from typing import Protocol

import time



class ScriptEvent(Protocol):
    
    def __init__(self) -> None:
        pass
    
    def call_callback(self):
        pass
    
    def raise_exception(self):
        pass
    
class RestartEventException(Exception):
    pass

class StopEventException(Exception):
    pass

class NestedStopEventException(Exception):
    pass

class  CompleteStopEventException(Exception):
    pass


class ScriptPauseEvent:
    
    def __init__(self ,
                 sleep_time : int ,
                 callback_before : bool ,
                 callback_func : typing.Callable[...,None] = None,
                 *args ,
                 **kwargs
                 ) :
        
        self.sleep_time = sleep_time
        self.callback_before = callback_before
        self.callback_func = (lambda : callback_func(*args,** kwargs)) if callback_func else None
    
    def call_callback_func(self):
        if self.callback_func :
            self.callback_func()
        
    
    def raise_exception(self) -> None:
        
        if self.callback_before :
            self.call_callback_func()
            time.sleep(self.sleep_time)
        else:
            time.sleep(self.sleep_time)
            self.call_callback_func()

class RestartEvent:
    
    def __init__(self,
                 callback_func : typing.Callable[...,None] = None,
                 *args ,
                 **kwargs):
        self.callback_func = lambda : callback_func(*args, **kwargs) if callback_func else None
    
    def call_callback_func(self):
        if self.callback_func :
            self.callback_func()
    
    def raise_exception(self) :
        
        self.call_callback_func()
        raise RestartEventException()

class StopEvent:
    
    def __init__(self,
                 callback_func : typing.Callable[...,None] = None,
                 *args ,
                 **kwargs):
        self.callback_func = lambda : callback_func(*args, **kwargs) if callback_func else None
    
    def call_callback_func(self):
        if self.callback_func :
            self.callback_func()
    
    def raise_exception(self) :
        
        self.call_callback_func()
        raise StopEventException()

class NestedStopEvent(Exception):
    def __init__(self,
                 callback_func : typing.Callable[...,None] = None,
                 *args ,
                 **kwargs):
        self.callback_func = lambda : callback_func(*args, **kwargs) if callback_func else None
    
    def call_callback_func(self):
        if self.callback_func :
            self.callback_func()
    
    def raise_exception(self) :
        
        self.call_callback_func()
        raise NestedStopEventException()

class CompleteStopEvent:
    
    def __init__(self,
                 callback_func : typing.Callable[...,None] = None,
                 *args ,
                 **kwargs):
        self.callback_func = lambda : callback_func(*args, **kwargs) if callback_func else None
    
    def call_callback_func(self):
        if self.callback_func :
            self.callback_func()
    
    def raise_exception(self) :
        
        self.call_callback_func()
        raise CompleteStopEventException()