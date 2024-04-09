from typing import Protocol
import time



class ScriptEvent(Protocol):
    
    def __init__(self) -> None:
        pass
    
    def raise_exception(self):
        pass
    
class RestartEventException(Exception):
    pass

class StopEventException(Exception):
    pass


class ScriptPauseEvent:
    
    def __init__(self , sleep_time : int) :
        
        self.sleep_time = sleep_time
    
    
    def raise_exception(self) -> None:
        
        time.sleep(self.sleep_time)


class RestartEvent:
    
    def __init__(self) -> None:
        pass
    
    def raise_exception(self) :
        
        raise RestartEventException()

class StopEvent:
    def __init__(self) -> None:
        pass
    
    def raise_exception(self) :
        
        raise StopEventException()