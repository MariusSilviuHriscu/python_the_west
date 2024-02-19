import typing
from dataclasses import dataclass
from saloon import QuestNotAcceptable,QuestAcceptError,QuestNotFinishable,QuestFinishError
from quest_requirements import Quest_requirement,Quest_requirement_duel_quest_npc


from the_west_inner.requests_handler import requests_handler


@dataclass
class LinearQuest():
    
    accepted : bool
    description : str
    is_duel : bool
    employer_id : str
    group_id : int
    quest_id : int
    requirements : list[dict]
    title : str
    finishable : bool
    def accept_quest(self, handler: requests_handler):
        payload={
                "groupid": self.group_id,
                "quest_id": self.quest_id
                }
        response = handler.post(window="linearquest",action="accept_linear_quest",payload = payload , use_h= True)
        if response['error'] :
            raise QuestAcceptError(f"Was not able to accept mission :{self.quest_id}.Return msg :{response['msg']}")
        
        self.accepted = True
    
    def _complete_quest(self,handler:requests_handler,reward_number:int = 0) -> dict:
        if not self.is_finishable:
            raise QuestNotFinishable(f"You tried to finish a quest that is not finishable! :{self.quest_id}")
        payload={
                "groupid": self.group_id,
                "quest_id": self.quest_id
                }
        response = handler.post(window="quest",action="finish_quest",payload=payload,use_h=True)
        
        return response['nextQuest']
    def load_from_response_dict(response_dict :dict) -> typing.Self:
        return LinearQuest(
            accepted = response_dict.get('accepted'),
            description = response_dict.get('description'),
            is_duel= response_dict.get('duel').get('isNPCDuel'),
            employer_id = response_dict.get('employerid'),
            group_id = response_dict.get('groupid'),
            quest_id = response_dict.get('questid'),
            requirements = response_dict.get('requirements'),
            title = response_dict.get('title'),
            finishable = False if response_dict.get('finishable') == 0 else True
        )
    def update_quest(self,handler:requests_handler) ->typing.Self :
        
        payload={
                "groupid": self.group_id,
                "quest_id": self.quest_id
                }
        
        response = handler.post(window = 'linearquest',action='update_linear_quest',action_name='mode',payload=payload)
        
        return LinearQuest.load_from_response_dict(response.get('quest'))
        
    def complete_quest(self, handler: requests_handler, reward_number: int = 0,depth_trial:int = 0) -> typing.Self:
        
        if depth_trial == 2:
            
            raise QuestFinishError('Tried to finished , refreshed and still not finishable')
        
        if not self.finishable:
            return self.update_quest(handler=handler).complete_quest(handler=handler,
                                                                     reward_number=reward_number,
                                                                     depth_trial = depth_trial + 1
                                                                     
                                                                     )
        
        return LinearQuest.load_from_response_dict(
                                                    response_dict= self._complete_quest(handler=handler,reward_number=reward_number)
                                                )


LINEAR_QUESTS_REQUIREMENTS = {
    0 : [Quest_requirement_duel_quest_npc(quest_id=0,solved = True)]
    
}

class LinearQuestManager():
    def __init__(self,handler:requests_handler):
        self.handler = handler
        self._current_quest = None
    
    def attempt_to_get_intro_tutorial_data(self , tutorial_id : int) -> tuple[bool,dict]:
        
        payload={
                "groupid": "0",
                "quest_id": tutorial_id
                }
        
        response = self.handler.post(window = 'linearquest',action='update_linear_quest',action_name='mode',payload=payload)
        
        return 'error' not in response,response
    
    def _get_current_quest(self) -> LinearQuest|None:
                
        for quest_id in LINEAR_QUESTS_REQUIREMENTS.keys():
            
            is_valid_quest , quest_dict = self.attempt_to_get_intro_tutorial_data(tutorial_id = quest_id)
            
            if is_valid_quest:
                
                return LinearQuest.load_from_response_dict(quest_dict)
    
    @property
    def current_quest(self) -> LinearQuest:
        
        if self._current_quest :
            return self._current_quest
        
        self._current_quest = self._get_current_quest()
        
        return self._current_quest
    