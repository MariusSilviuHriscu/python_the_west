import typing
from dataclasses import dataclass

from requests_handler import requests_handler
from quest_requirements import Quest_requirement

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
    requirement_list: list[dict]
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
    quest_reward_options : dict[int,dict] = None
    
    
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
    
    def get_requirements(self , requirement_parser_func : typing.Callable[[list[dict]],list[Quest_requirement]]):
        return requirement_parser_func(self.requirement_list)
    
    
    @staticmethod
    def load_from_response_dict(response_dict:dict) -> typing.Self:
        return Quest(quest_id = response_dict.get('id'),
                     solo_title = response_dict.get('soloTitle'),
                     group_title = response_dict.get('groupTitle'),
                     group_id = response_dict.get('group'),
                     group_title_full = response_dict.get('title'),
                     requirement_list = response_dict.get('requirements'),
                     is_duel = response_dict.get('duel').get('isNPCDuel'),
                     is_acceptable = response_dict.get('acceptable'),
                     is_accepted = response_dict.get('accepted'),
                     is_accessable = response_dict.get('accessable'),
                     is_finishable = response_dict.get('finishable'),
                     description = response_dict.get('description'),
                     redraw_map = response_dict.get('redrawMap'),
                     is_challenge = response_dict.get('isChallenge'),
                     employer_key = response_dict.get('employer'),
                     is_completed = all((x.get('solved') for x in response_dict.get('requirements'))),
                     employer_coords = response_dict.get('employer_coords'),
                     quest_reward_options = response_dict.get('questRewardsOptions') if response_dict.get('questRewardsOptions') else None
                     )
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
    
    def get_quest_employer(self,handler:requests_handler) -> Quest_employer:
        return get_quest_employer_by_key(handler=handler,employer_key=self.key)

def get_saloon_employer(handler:requests_handler) -> list[Quest_employer_saloon]:
    
    response = handler.post(window='building_quest')
    
    if 'questEmployer' not in response:
        raise Exception('Saloon could not be found...')
    
    employer_data : list[dict] = response['questEmployer']
    
    return [Quest_employer_saloon(key=employer['key'],name=employer['name']) for employer in employer_data]