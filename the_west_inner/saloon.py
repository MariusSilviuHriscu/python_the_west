import typing
from dataclasses import dataclass

from requests_handler import requests_handler
from quest_requirements import Quest_requirement
from gold_finder import parse_map_for_quest_employers

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
class QuestNotCompletedError(Exception):
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
        self.quest_dict ={x.quest_id : x for x in self.quest_list}
    def get_by_id(self,search_id:int):
        if search_id not in self.quest_dict:
            raise QuestNotFound(f"Didn't find the required id :{search_id}")
        return self.quest_dict[search_id]
    def append(self,quest_list: list[Quest]):
        
        self.quest_list.extend(quest_list)
        self.quest_dict = {**self.quest_dict,**{x.quest_id : x for x in self.quest_list}}
    def __contains__(self , quest_id:int) -> bool:
        
        return quest_id in self.quest_dict

    
class Quest_employer():
    def __init__(self,key:str,name:str,x:int,y:int,quest_list:Quest_list):
        self.key = key
        self.name = name
        self.x = x
        self.y = y
        self.quest_list = quest_list
    def get_quest_by_id(self,quest_id:int) -> Quest:
        return self.quest_list.get_by_id(search_id=quest_id)
    def reload_data(self,handler:requests_handler):
        self = get_quest_employer_by_key(handler=handler,
                                         employer_key = self.key,
                                         employer_coords = (self.x,self.y)
                                         )

class EmployerNotCorresponding(Exception):
    pass

def get_quest_employer_by_key(handler:requests_handler,employer_key:str,employer_coords:tuple[int,int]= None) -> Quest_employer:
    payload = {"employer":employer_key}
    if employer_coords is not None:
        payload["x"] = employer_coords[0]
        payload["y"] = employer_coords[1]
    result = handler.post(window="quest_employer",action='',payload=payload)
    if 'employer' not in result or "key" not in result['employer'] or result['employer']['key'] != employer_key:
        raise EmployerNotCorresponding(f"The result employer key and search key do not correspond : {employer_key}")
    return Quest_employer(
        key = result.get('key'),
        name = result.get('name'),
        x = result.get('x'),
        y = result.get('y'),
        quest_list = Quest_list(
                                quest_list= [Quest.load_from_response_dict(response_dict=x) for x in result.get('open')]
                                )
    )

    
class Quest_employer_saloon():
    
    def __init__(self,key:str,name:str,location:tuple[int,int]| None = None):
        self.key = key
        self.name = name
        self.location = location
    def get_quest_employer(self,handler:requests_handler) -> Quest_employer:
        return get_quest_employer_by_key(handler=handler,employer_key=self.key,employer_coords=self.location)

def get_saloon_employer(handler:requests_handler) -> list[Quest_employer_saloon]:
    
    response = handler.post(window='building_quest',action='')
    
    if 'questEmployer' not in response:
        raise Exception('Saloon could not be found...')
    employer_data : list[dict] = response['questEmployer']
    
    return [Quest_employer_saloon(key=employer['key'],name=employer['name']) for employer in employer_data]

def get_available_map_employers(handler:requests_handler) -> list[Quest_employer_saloon]:
    
    map_employers_raw_map_data = parse_map_for_quest_employers(handler=handler)
    
    employer_list = []
    for location_data in map_employers_raw_map_data:
        x = location_data.get('x')
        y = location_data.get('y')
        employers = location_data.get('employer')
        
        employer_list.extend(
            (Quest_employer_saloon(key = employer_data.get('key'),
                                   name= employer_data.get('name'),
                                   location = (x,y)
                                   )
                for employer_data in employers if employer_data.get('visible'))
        )
    return employer_list

class EmployerNotFoundException(Exception):
    pass

class QuestEmployerDataList():
    def __init__(self , quest_employers : list[Quest_employer]):
        self.quest_employers = quest_employers

    def has_available_quest(self,quest_id:int) -> bool:
        
        for quest_employer in self.quest_employers:
            if quest_id in quest_employer.quest_list:
                return True
        return False
    def get_employer_by_quest_id(self,quest_id : int) ->Quest_employer:
        for quest_employer in self.quest_employers:
            if quest_id in quest_employer.quest_list:
                return quest_employer
        raise EmployerNotFoundException(f"Couldn't find quest employer that has : {quest_id} quest ! ") 

def load_all_available_quest_employers_data_list(handler:requests_handler) -> QuestEmployerDataList:
    
    saloon_employers = get_saloon_employer(handler=handler)
    available_map_employers = get_available_map_employers(handler=handler)
    
    return QuestEmployerDataList(
        quest_employers= [x.get_quest_employer(handler=handler) for x in saloon_employers + available_map_employers]
    )

QuestIDType = int
QuestGroupIDType = int

SolvedQuestGroupDictType = dict[QuestGroupIDType:dict[QuestIDType:str]]


class SolvedQuestData:
    
    def __init__(self , solved_quest_group_dict : SolvedQuestGroupDictType):
        
        self.solved_quest_group_dict = solved_quest_group_dict
    
    def has_solved(self,quest_id) -> bool:
        
        return any(
            (quest_id in x for x in self.solved_quest_group_dict.values())
            )
    def __contains__(self,quest_id:int):
        
        return self.has_solved(quest_id=quest_id)

class SolvedQuestManager:
    def __init__(self, handler: requests_handler):
        self.handler = handler
        self._solved_quest_data = None
    
    
    
    def _process_data(self,response_dict : dict) -> SolvedQuestData:
        
        group_dict = {}
        for group_id,group_data in response_dict.items():
            quest_data = group_data.get('quests')
            if isinstance(quest_data,list):
                quest_data = {quest_id:quest_title for quest_id,quest_title in enumerate(quest_data)}
            group_dict.update({group_id : quest_data})
        return SolvedQuestData(solved_quest_group_dict = group_dict)
            
    def load_solved_quests(self) -> SolvedQuestData:
        
        response = self.handler.post(window='building_quest',action='get_solved_groups',action_name='mode')
        
        if 'solved' not in response:
            
            raise Exception('Could not load solved quests!')

        
        return  self._process_data(response_dict = response['solved'])
    def update_data(self):
        
        self._solved_quest_data = self.load_solved_quests()
    
    @property
    def solved_quest_data(self) -> SolvedQuestData:
        if not self._solved_quest_data:
            self.update_data()
        return self._solved_quest_data
    
    def has_completed_quest(self,quest_id: int) -> bool:
        
        return quest_id in self.solved_quest_data