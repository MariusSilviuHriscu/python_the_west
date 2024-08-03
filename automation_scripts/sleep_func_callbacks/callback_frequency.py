import random
from datetime import datetime, timedelta ,time
from typing import Protocol
import typing

class FrequencyRule(Protocol):
    """
    A protocol defining the methods for a frequency rule.

    Methods:
    - __init__: Initializes an instance of the frequency rule.
    - should_run: Checks if the rule allows execution.
    """
    def __init__(self):
        pass
    
    def should_run(self) -> bool:
        pass

class AlwaysRunRule():
    """
    A rule that always allows execution.

    Methods:
    - __init__: Initializes an instance of the rule.
    - should_run: Checks if the rule allows execution (always returns True).
    """
    def __init__(self):
        pass
    
    def should_run(self) -> bool:
        return True

class RandomRunRule():
    """
    A rule that allows execution with a certain probability.

    Methods:
    - __init__: Initializes an instance of the rule with a specified run chance.
    - should_run: Checks if the rule allows execution based on random probability.
    """
    def __init__(self, run_chance: float):
        self.run_chance = run_chance

    def should_run(self) -> bool:
        return random.random() < self.run_chance

class RunAfterNRule():
    """
    A rule that allows execution after a certain number of calls.

    Methods:
    - __init__: Initializes an instance of the rule with a specified limit.
    - should_run: Checks if the rule allows execution based on the call count.
    """
    def __init__(self, limit: int):
        self.limit = limit
        self.counter = 0
    
    def should_run(self) -> bool:
        if self.limit > self.counter :
            self.counter += 1
            return False
        return True

class IntervalRule:
    """
    A rule that allows execution at regular intervals with optional repetition.

    Methods:
    - __init__: Initializes an instance of the rule with interval, run times, and repeat times.
    - should_run: Checks if the rule allows execution based on the intervals and repetition.
    """
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

class EveryNSeconds():
    """
    A rule that allows execution every N seconds.

    Methods:
    - __init__: Initializes an instance of the rule with a specified time duration.
    - should_run: Checks if the rule allows execution based on time intervals.
    """
    def __init__(self, time_seconds: int):
        self.duration = timedelta(seconds=time_seconds)
        self.time_stamp = datetime.now()

    def should_run(self) -> bool:
        current_time = datetime.now()

        if current_time - self.time_stamp >= self.duration:
            self.time_stamp = current_time
            return True
        else:
            return False

class CallableRunRule():
    """
    A rule based on a custom callable condition.

    Methods:
    - __init__: Initializes an instance of the rule with a callable condition.
    - should_run: Checks if the rule allows execution based on the callable condition.
    """
    def __init__(self, condition_callable: typing.Callable[[], bool]):
        self.condition_callable = condition_callable

    def should_run(self) -> bool:
        return self.condition_callable()

class CombinedRule():
    """
    A rule that combines multiple rules using logical AND.

    Methods:
    - __init__: Initializes an instance of the rule with multiple sub-rules.
    - should_run: Checks if all sub-rules allow execution (logical AND).
    """
    def __init__(self, *rules):
        self.rules = rules

    def should_run(self) -> bool:
        # Combine the results of individual rules using logical AND
        return all(rule.should_run() for rule in self.rules)


class RunOnceThenStopRule():
    
    """
    A rule that allows execution once and then stops.

    Methods:
    - __init__: Initializes an instance of the rule with a callable condition.
    - should_run: Checks if the rule allows execution based on the callable condition.
    """
    def __init__(self , condition_callable: typing.Callable[[], bool]):
        self.condition_callable = condition_callable
        self.has_run = False
    
    def should_run(self) -> bool:
        
        if self.has_run:
            return False
        
        checked_value = self.condition_callable()
        
        if checked_value:
            
            self.has_run = True
            return True
        
        return False

class DatetimeIntervalRule():
    """
    A rule that allows execution only within a specified time interval in a 24-hour period.

    Methods:
    - __init__: Initializes an instance of the rule with start and end times.
    - should_run: Checks if the rule allows execution based on the current time.
    """
    def __init__(self, start_hour: int, start_minute: int, end_hour: int, end_minute: int):
        self.start_time = time(start_hour, start_minute)
        self.end_time = time(end_hour, end_minute)

    def should_run(self) -> bool:
        current_time = datetime.now().time()
        
        if self.start_time <= self.end_time:
            # Interval does not span midnight
            return self.start_time <= current_time <= self.end_time
        else:
            # Interval spans midnight
            return current_time >= self.start_time or current_time <= self.end_time