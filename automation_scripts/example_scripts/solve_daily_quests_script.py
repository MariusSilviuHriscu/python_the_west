from the_west_inner.requests_handler import requests_handler
from the_west_inner.player_data import Player_data

from the_west_inner.saloon import get_quest_employer_by_key

class QuestIDSuite:
    
    def __init__(self, 
                 easy_quest_id : int,
                 medium_quest_id : int,
                 hard_quest_id : int
                 ) :
        
        self.easy_quest_id = easy_quest_id
        self.medium_quest_id = medium_quest_id
        self.hard_quest_id = hard_quest_id
    
    @property
    def easy(self) -> int:
        return self.easy_quest_id
    @property
    def medium(self) -> int:
        return self.medium_quest_id
    @property
    def hard(self) -> int:
        return self.hard_quest_id
    
    def get_quests(self,reversed : bool = False) -> list[int]:
        if reversed:
            return [self.hard , self.medium , self.easy]
        return [self.easy , self.medium , self.hard]

REPEATABLE_CRAFTING_QUEST = {
    2 : QuestIDSuite(
        easy_quest_id = 2043365,
        medium_quest_id = 2043369,
        hard_quest_id = 2043373
    )
}

def load(handler:requests_handler):
    paper_quests = get_quest_employer_by_key(handler=handler,
                                              employer_key = 'paper'
                                              )
    paper_quests.quest_list
class RepeatableQuestsSolver:
    
    def __init__(self,
                 handler : requests_handler,
                 player_data : Player_data
                 ):
        
        self.handler = handler
        self.player_data = player_data
        self.crafting_id = player_data.profession_id
        self.crafting_quest_data = REPEATABLE_CRAFTING_QUEST
        
        self._quest_employer = None
    @property
    def quest_list(self):
        if self._quest_employer is None:
            self._quest_employer = get_quest_employer_by_key(handler=self.handler,
                                              employer_key = 'paper'
                                              )
        return self._quest_employer.quest_list
    def solve_crafting_quests(self) -> int:
        target_quest_suite : QuestIDSuite|None = self.crafting_quest_data.get(self.crafting_id,None)
        if target_quest_suite is None:
            raise Exception('The target repeatable quest stuff is not implemented !')
        
        quest_list = target_quest_suite.get_quests(reversed=True)
        
        for quest_id in quest_list:
            
            quest = self.quest_list.get_by_id(search_id=quest_id)
            
            if not quest.is_completed :
                continue
            
            if not quest.is_accepted :
                
                quest.accept_quest(handler=self.handler)
            
            quest.complete_quest(handler=self.handler)
            return quest_id
        
    def solve_solved_repeatable_quests(self) -> list[int]:
        
        target_quest_suite : QuestIDSuite | None = self.crafting_quest_data.get( self.crafting_id,
                                                                                QuestIDSuite(None,None,None)
                                                                                )
        
        crafting_quest_list = target_quest_suite.get_quests()
        
        
        completed_quest_list = []
        for quest in self.quest_list:
            
            if not quest.is_completed or quest.quest_id in crafting_quest_list:
                continue
            
            if not quest.is_accepted:
                quest.accept_quest(handler=self.handler)
            
            quest.complete_quest(handler=self.handler)
            completed_quest_list.append(quest.quest_id)
        
        return completed_quest_list