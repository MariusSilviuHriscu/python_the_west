import typing

from the_west_inner.requests_handler import requests_handler
from the_west_inner.linear_quest_manager import LinearQuestManager,LinearQuest

class LinearQuestSolver :
    
    def __init__(self ,
                 handler: requests_handler ,
                 linear_quest_manager: LinearQuestManager):
        
        self.handler = handler
        self.linear_quest_manager = linear_quest_manager

        self.current_quest = linear_quest_manager.current_quest
    
    def solve_current_quest(self) -> LinearQuest|None :
        
        if self.current_quest.accepted and self.current_quest.finishable:
            
            return self.current_quest.complete_quest(handler=self.handler)
        
        