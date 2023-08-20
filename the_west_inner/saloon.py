import typing
from dataclasses import dataclass

from requests_handler import requests_handler
from quest_requirements import Quest_requirement,Quest_Reward

class QuestNotAcceptable(Exception):
    pass
class QuestAcceptError(Exception):
    pass
class QuestNotAccepted(Exception):
    pass
class QuestCancelError(Exception):
    pass
class QuestNotFinishable(Exception):
    pass
class QuestFinishError(Exception):
    pass
@dataclass
class Quest():
    quest_id:int
    solo_title:str
    group_title:str
    group_id : int
    group_title_full : str
    requirement_list: list[Quest_requirement]
    is_duel : bool
    is_acceptable : bool
    is_accepted : bool
    is_accessable : bool
    is_finishable : bool
    description : str
    redraw_map : bool
    is_challenge : bool
    employer_key : str
    is_completed : bool = False
    employer_coords : bool| tuple[int] = False
    quest_reward_options : dict[int,Quest_Reward] ={}
    
    
    def accept_quest(self,handler:requests_handler):
        if not self.is_acceptable:
            raise QuestNotAcceptable(f"This quest cannot be accepted. :{self.quest_id}")
        response = handler.post(window="quest",action="accept_quest",payload={"quest_id": self.quest_id},use_h= True)
        if response['error'] :
            raise QuestAcceptError(f"Was not able to accept mission :{self.quest_id}.Return msg :{response['msg']}")
        
        self.is_accepted = True
        self.is_acceptable = False
        self.is_finishable = response["finishable"]
    def cancel_quest(self,handler:requests_handler):
        if not self.is_accepted:
            raise QuestNotAccepted(f"You tried to cancel a quest that is not accepted! :{self.quest_id}")
        
        response = handler.post(window="quest",action="cancel_quest",payload={"quest_id": self.quest_id},use_h=True)
        
        if response['error']:
            raise QuestCancelError(f"Was not able to cancel mission :{self.quest_id}.Return msg :{response['msg']}")
        
        self.is_accepted = False
        self.is_acceptable = True
        self.is_finishable = False
    def complete_quest(self,handler:requests_handler,reward_number:int = 0):
        if not self.is_finishable:
            raise QuestNotFinishable(f"You tried to finish a quest that is not finishable! :{self.quest_id}")
        
        response = handler.post(window="quest",action="finish_quest",payload={"quest_id": self.quest_id ,"reward_option_id": f"{reward_number}"})
        
        if response['error']:
            raise QuestFinishError(f"Was not able to finish mission :{self.quest_id}.Return msg :{response['msg']}")
        
        self.is_completed = True
        
class QuestNotFound(Exception):
    pass
class Quest_list():
    def __init__(self,quest_list:list[Quest]):
        self.quest_list = quest_list
        self.quest_dict ={quest_id:quest_data for quest_id,quest_data in self.quest_list.items()}
    def get_by_id(self,search_id:int):
        if search_id not in self.quest_dict:
            raise QuestNotFound(f"Didn't find the required id :{search_id}")
        return self.quest_dict[search_id]

    
class Quest_employer():
    def __init__(self,key:str,name:str,x:int,y:int,quest_list:Quest_list):
        self.key = key
        self.name = name
        self.x = x
        self.y = y
        self.quest_list = quest_list

class EmployerNotCorresponding(Exception):
    pass
def get_quest_employer_by_key(handler:requests_handler,employer_key:str,employer_coords:tuple[int]= None) -> Quest_employer:
    payload = {"employer":employer_key}
    if employer_coords is not None:
        payload["x"] = employer_coords[0]
        payload["y"] = employer_coords[1]
    result = handler.post(window="quest_employer",payload=payload)
    
    if  "key" not in result or result['key'] != employer_key:
        raise EmployerNotCorresponding(f"The result employer key and search key do not correspond : {employer_key}")
    
    return Quest_employer

    
class Quest_employer_saloon():
    
    def __init__(self,key:str,name:str):
        self.key = key
        self.name = name
    
    def get_quest_employer(self) -> Quest_employer:
        pass