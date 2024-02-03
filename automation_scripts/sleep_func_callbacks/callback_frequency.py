import random
from typing import Protocol

class FrequencyRule(Protocol):
    def __init__(self):
        pass
    def should_run(self) -> bool:
        pass

class AlwaysRunRule():
    
    def __init__(self) :
        pass
    
    def should_run(self) -> bool:
        return True

class RandomRunRule():
    
    def __init__(self, run_chance: float):
        self.run_chance = run_chance

    def should_run(self) -> bool:
        return random.random() < self.run_chance

class RunAfterNRule():
    
    def __init__(self,limit:int):
        self.limit = limit
        self.counter = 0
    
    def should_run(self) -> bool:
        
        if self.limit > self.counter :
            self.counter += 1
            return False
        return True
class IntervalRule:
    def __init__(self, interval: int, run_times: int = 1, repeat_times: int | None = None):
        self.interval = interval
        self.run_times = run_times
        self.repeat_times = repeat_times
        self.counter = 0
        self.repeat_times_counter = 0
        self.temp_run_times = 0

    def should_run(self) -> bool:
        self.counter += 1

        if self.repeat_times is None or self.repeat_times_counter < self.repeat_times:
            if self.counter % self.interval == 0:
                self.temp_run_times += 1

                if self.temp_run_times >= self.run_times:
                    self.temp_run_times = 0
                    self.repeat_times_counter += 1
                    return True

        return False
class CombinedRule():
    def __init__(self, *rules):
        self.rules = rules

    def should_run(self) -> bool:
        # Combine the results of individual rules using logical AND
        return all(rule.__bool__() for rule in self.rules)
