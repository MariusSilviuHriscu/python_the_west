import typing
from dataclasses import dataclass
from saloon import QuestNotAcceptable,QuestAcceptError,QuestNotFinishable,QuestFinishError
from the_west_inner.quest_requirements import (
                    Quest_requirement,
                    Quest_requirement_duel_quest_npc,
                    Quest_requirement_duel_npc,
                    Quest_requirement_get_n_skill_points,
                    Quest_requirement_work_n_times,
                    Quest_requirement_get_n_attribute_points,
                    Quest_requirement_item_to_hand_work_product_seconds,
                    Quest_requirement_equip_item
                    )


from the_west_inner.requests_handler import requests_handler


@dataclass
class LinearQuest():
    
    accepted : bool
    description : str
    is_duel : bool
    employer_id : str
    group_id : int
    quest_id : int
    requirements : list[dict|Quest_requirement]
    title : str
    finishable : bool
    def accept_quest(self, handler: requests_handler):
        payload={
                "groupid": self.group_id,
                "questid": self.quest_id
                }
        response = handler.post(window="linearquest",action="accept_linear_quest",payload = payload , use_h= True)
        if 'error' in response and response['error'] :
            raise QuestAcceptError(f"Was not able to accept mission :{self.quest_id}.Return msg :{response['msg']}")
        self.accepted = True
    
    def _complete_quest(self,handler:requests_handler,reward_number:int = 0) -> dict:
        if not self.finishable and not any((isinstance(x,Quest_requirement_duel_quest_npc) for x in self.requirements)):
            raise QuestNotFinishable(f"You tried to finish a quest that is not finishable! :{self.quest_id}")
        payload={
                "groupid": self.group_id,
                "questid": self.quest_id
                }
        response = handler.post(window="linearquest",action="finish_linear_quest",payload=payload,use_h=True)
        return response['nextQuest']
    def load_from_response_dict(response_dict :dict|None) -> typing.Self | None:
        if response_dict is None:
            return None

        return LinearQuest(
            accepted = response_dict.get('accepted'),
            description = response_dict.get('description'),
            is_duel= response_dict.get('duel').get('isNPCDuel'),
            employer_id = response_dict.get('employerid'),
            group_id = response_dict.get('groupid'),
            quest_id = response_dict.get('questid'),
            requirements = LINEAR_QUESTS_REQUIREMENTS[response_dict.get('questid')],
            title = response_dict.get('title'),
            finishable = False if response_dict.get('finishable') == 0 else True
        )
    def update_quest(self,handler:requests_handler) ->typing.Self :
        
        payload={
                "groupid": self.group_id,
                "questid": self.quest_id
                }
        
        response = handler.post(window = 'linearquest',action='update_linear_quest',action_name='mode',payload=payload)
        
        return LinearQuest.load_from_response_dict(response.get('quest'))
        
    def complete_quest(self, handler: requests_handler, reward_number: int = 0,depth_trial:int = 0) -> typing.Self|None:
        
        if depth_trial == 2:
            
            raise QuestFinishError('Tried to finished , refreshed and still not finishable')
        
        if not self.finishable and not any((isinstance(x,Quest_requirement_duel_quest_npc) for x in self.requirements)) :
            return self.update_quest(handler=handler).complete_quest(handler=handler,
                                                                     reward_number=reward_number,
                                                                     depth_trial = depth_trial + 1
                                                                     
                                                                     )
        
        return LinearQuest.load_from_response_dict(
                                                    response_dict= self._complete_quest(handler=handler,reward_number=reward_number)
                                                )


LINEAR_QUESTS_REQUIREMENTS = {
    0 : [Quest_requirement_duel_quest_npc(quest_id=0,solved=False)],
    1 : [Quest_requirement_duel_npc(quest_id=1,solved=False)],
    2 : [Quest_requirement_get_n_skill_points(target_number=2,skill_key='health',solved = False)],
    3 : [Quest_requirement_work_n_times(work_id = 128,required_work_times=1,solved=False)],
    4 : [Quest_requirement_work_n_times(work_id=130,required_work_times=2,solved=False)],
    5 : [Quest_requirement_get_n_attribute_points(target_number=2,attribute_key='strength',solved=False)],
    6 : [Quest_requirement_item_to_hand_work_product_seconds(item_id=2160000,number=1,quest_id=6,solved=False)],
    7 : [],
    8 : [Quest_requirement_equip_item(item_id=41031000,solved=False)],
    9 : [Quest_requirement_item_to_hand_work_product_seconds(item_id=2162000,number=1,quest_id=9,solved=False)],
    10 :[]
}

class LinearQuestManager():
    def __init__(self,handler:requests_handler):
        self.handler = handler
        self._current_quest = None
        self.is_completed = False
    def attempt_to_get_intro_tutorial_data(self , tutorial_id : int) -> tuple[bool,dict]:
        payload={
                "groupid": "1",
                "quest_id": tutorial_id
                }
        
        response = self.handler.post(window = 'linearquest',action='update_linear_quest',action_name='mode',payload=payload)
        return 'error' not in response,response
    
    def _get_current_quest(self) -> LinearQuest|None:
                
        for quest_id in LINEAR_QUESTS_REQUIREMENTS.keys():
            
            is_valid_quest , quest_dict = self.attempt_to_get_intro_tutorial_data(tutorial_id = quest_id)
            
            if is_valid_quest:
                
                return LinearQuest.load_from_response_dict(quest_dict['quest'])
        self.is_completed = True
    
    @property
    def current_quest(self) -> LinearQuest:
        
        if self._current_quest :
            return self._current_quest
        
        self._current_quest = self._get_current_quest()
        
        return self._current_quest
    def accept_quest(self):
        if not self._current_quest.accepted:
            self._current_quest.accept_quest(handler=self.handler)
    
    def complete_quest(self,reward_option : int = 0) :
        
        next = self.current_quest.complete_quest(handler=self.handler,
                                          reward_number = reward_option
                                          )
        
        if next is None:
            self.is_completed = True
            self._current_quest = None
            return True
        
        self._current_quest = next
    