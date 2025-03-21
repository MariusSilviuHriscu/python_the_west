import time
import typing
from enum import Enum
from dataclasses import dataclass, fields
import datetime

from the_west_inner.requests_handler import requests_handler
from the_west_inner.equipment import Equipment_manager,Equipment
from the_west_inner.misc_scripts import turn_game_time_to_datetime
from the_west_inner.player_data import Player_data

STANCE_NUM : int = 4
class DuelTargetStanceEnum(Enum):
    
    HEAD = 'head'
    RIGHT_SHOULDER = 'rightshoulder'
    LEFT_SHOULDER = 'leftshoulder'
    LEFT_ARM = 'leftarm'
    RIGHT_ARM = 'rightarm'

class DuelDodgeStanceEnum(Enum):
    
    AIM = 'aim'
    DUCK = 'duck'
    LEFT = 'left'
    RIGHT = 'right'

class PlayerDuelStance():
    def __init__(self, 
                 target_stance_list : list[DuelTargetStanceEnum],
                 dodge_stance_list : list[DuelDodgeStanceEnum]):
        if len(target_stance_list) != STANCE_NUM or len(target_stance_list) != STANCE_NUM :
            raise ValueError(f'There can only be {STANCE_NUM} maximum stances . You have {len(target_stance_list)} and {len(dodge_stance_list)}')
        self.target_stance_list = target_stance_list
        self.dodge_stance_list = dodge_stance_list
    
    @property
    def settings(self) -> dict[str,str]:
        
        aim_dict = {'aim':
                            {str(index + 1) : value.value for index,value in enumerate(self.target_stance_list)}
                    }
        
        dodge_dict= {'dodge':
                            {str(index + 1) : value.value for index,value in enumerate(self.dodge_stance_list)}
                    }
        
        return {**aim_dict,**dodge_dict}
    def _set_target_stance(self,list_index:int,stance:DuelTargetStanceEnum):
        
        self.target_stance_list[list_index] = stance
        
    def _set_dodge_stance(self,list_index:int,stance:DuelDodgeStanceEnum):
        
        self.dodge_stance_list[list_index] = stance
        
    # 1 based index !!
    def change_target_stance(self,handler : requests_handler , stance_index : int , stance:DuelTargetStanceEnum) :
        
        if stance_index == 0:
            raise ValueError("Duel target stance index starts from 1 . It can't be 0")
        
        current_settings = self.settings
        
        new_settings = current_settings['aim'][str(stance_index)] = stance.value
        
        result = handler.post(window='duel',action = 'save_settings',payload=new_settings,use_h=True)
        
        if not result['error']:
            
            raise Exception('Something went wrong when trying to save the new duel settings!')

        self._set_target_stance(
            list_index = stance_index - 1,
            stance = stance
        )
    def change_dodge_stance(self,handler : requests_handler , stance_index : int , stance:DuelTargetStanceEnum) :
        
        if stance_index == 0:
            raise ValueError("Duel target stance index starts from 1 . It can't be 0")
        
        current_settings = self.settings
        
        new_settings = current_settings['dodge'][str(stance_index)] = stance.value
        
        result = handler.post(window='duel',action = 'save_settings',payload=new_settings,use_h=True)
        
        if not result['error']:
            
            raise Exception('Something went wrong when trying to save the new duel settings!')

        self._set_dodge_stance(
            list_index = stance_index - 1,
            stance = stance
        )

class DuelResultData:
    
    def __init__(self , 
                 won : bool,
                 ko : bool,
                 experience : int,
                 money : int,
                 attacker_dead : bool):
        
        self.won = won
        self.ko = ko
        self.experience = experience
        self.money = money
        self.attacker_dead = attacker_dead
    
    @staticmethod
    def load_from_dict(result_dict : dict[str,typing.Any] , attacker_dead : bool) -> typing.Self:
        
        result_dict = result_dict.get('resultData')
        
        won = result_dict.get('won')
        ko = result_dict.get('ko') == 'def'
        experience = result_dict.get('winner').get('xp') if won else 0
        money = result_dict.get('winner').get('dollars') if won else 0
        
        return DuelResultData(
            won = won,
            ko=ko,
            experience = experience,
            money = money,
            attacker_dead = attacker_dead
        )
    def __str__(self):
        
        return f'DuelResult(Won: {self.won}, KO: {self.ko}, Experience: {self.experience}, Money: {self.money}, Attacker Dead: {self.attacker_dead})'
    
    def __repr__(self):
        
        return self.__str__()

@dataclass
class DuelNpcData:
    duelnpc_id: int
    health: int
    npc_name: str
    picture: str
    arrival_delta: float
    npc_level: int
    intelligence: int
    difficulty: int
    punch: int
    tough: int
    dodge: int
    reflex: int
    aim: int
    shot: int
    tactic: int
    appearance: int
    weapon_id: int
    arrival: float

    @staticmethod
    def load_from_dict(npc_data_dict: typing.Dict[str, typing.Any]) -> typing.Self:
        # Extract the fields from the data class
        fields_dict = {field.name: field for field in fields(DuelNpcData)}
        
        # Create a dictionary with field names and their corresponding values
        valid_fields = {name: npc_data_dict.get(name) for name in fields_dict}
        
        # Use the dictionary to create an instance of DuelNpcData
        return DuelNpcData(**valid_fields)

class NpcDuelException(Exception):
    pass

class NpcDuelList :
    def __init__(self ,
                 npc_duel_motivation : float ,
                 difficulty : int, 
                 npc_list : list[DuelNpcData],
                 remaining_time : float,
                 arrival_delay : float | int = 0
                 ):
        
        self._npc_duel_motivation = npc_duel_motivation
        self._difficulty = difficulty
        self._npc_list = npc_list
        self.arrival_delay = arrival_delay
        self.end_time = datetime.datetime.now() + datetime.timedelta(seconds=remaining_time)
        self.arrival_delay = arrival_delay
    def _reload_data(self,handler:requests_handler) :
        
        response = handler.post(window='duel',action='reload',use_h=True)
        
        difficulty = response.get('npcs',{}).get('difficulty')
        arrival_delay = response.get('npcs',{}).get('arrival_delay')
        
        npc_data_dict = response.get('npcs').get('npcs')
        remaining_time = response.get('npcs').get('remaining_time')
        
        self.__init__(npc_duel_motivation=self._npc_duel_motivation,
                      difficulty = difficulty ,
                      npc_list = [DuelNpcData.load_from_dict(npc_data_dict=x) for x in npc_data_dict],
                      remaining_time = int(remaining_time),
                    arrival_delay = arrival_delay
                      )
    
    def __contains__(self, npc_id:int):
        
        return npc_id in [x.duelnpc_id for x in self._npc_list]
    
    
    def has_to_reload(self) -> bool:
        
        return datetime.datetime.now() >= self.end_time
    
    def get_npc_list(self,handler : requests_handler) -> list[DuelNpcData]:
        
        if self.has_to_reload():
            
            self._reload_data(handler = handler)
        
        return self._npc_list
    
    def get_difficulty(self,handler : requests_handler) -> int:
        
        if self.has_to_reload():
            
            self._reload_data(handler = handler)
        
        return self._difficulty
    def get_npc_by_id(self,npc_id:int) -> DuelNpcData:
        
        return next((npc for npc in self._npc_list if npc.duelnpc_id == npc_id),None)
    def get_npc_by_smallest(self, key: str) -> int:
        # Create a dictionary with NPC IDs as keys and corresponding values for the specified key
        value_dict = {npc.duelnpc_id: getattr(npc, key) for npc in self._npc_list}

        # Find the NPC ID with the smallest value for the specified key
        min_npc_id = min(value_dict, key=lambda npc_id: value_dict[npc_id])
        return min_npc_id
    def get_npc_by_biggest(self, key: str) -> int:
        # Create a dictionary with NPC IDs as keys and corresponding values for the specified key
        value_dict = {npc.duelnpc_id: getattr(npc, key) for npc in self._npc_list}

        # Find the NPC ID with the smallest value for the specified key
        max_npc_id = max(value_dict, key=lambda npc_id: value_dict[npc_id])
        return max_npc_id
    def get_npc_by_smallest(self, key: str) -> typing.Optional[int]:
        # Filter only NPCs that have arrived
        available_npcs = [npc for npc in self._npc_list if datetime.datetime.now().timestamp() >= npc.arrival]
        
        if not available_npcs:
            return None  # No valid NPCs available

        # Find the NPC ID with the smallest value for the specified key
        return min(available_npcs, key=lambda npc: getattr(npc, key)).duelnpc_id

    def get_npc_by_biggest(self, key: str) -> typing.Optional[int]:
        # Filter only NPCs that have arrived
        available_npcs = [npc for npc in self._npc_list if datetime.datetime.now().timestamp() >= npc.arrival]
        
        if not available_npcs:
            return None  # No valid NPCs available

        # Find the NPC ID with the largest value for the specified key
        return max(available_npcs, key=lambda npc: getattr(npc, key)).duelnpc_id
        
    def _duel_npc(self,handler:requests_handler,npc_id:int):
        
        response = handler.post(window = 'duel',action = 'duel_npc',payload = {'duelnpc_id': f'{npc_id}'},use_h=True)
        if response.get('error',False) == True:
            
            raise NpcDuelException(f'Something went wrong when trying to duel an npc {response}')
        
        return response
    
    def duel_npc(self, npc_id : int,handler : requests_handler) -> DuelResultData:
        
        if npc_id not in self:
            raise ValueError('This npc is not available for duel!')
        
        data = self._duel_npc(handler = handler,npc_id = npc_id)
        
        self._npc_duel_motivation = data.get('motivation_npc')
        
        return DuelResultData.load_from_dict(result_dict = data.get('data') , attacker_dead = data.get('attacker_died',False))
    
    def is_ready(self, npc_id: int) -> bool:
        
        return self.arrival_delay - self.get_npc_by_id(npc_id).arrival_delta < 0
    
    def get_npc_arrival_time(self, npc_id: int) -> int | float | None:
        
        if self.is_ready(npc_id):
            return None
        
        return self.arrival_delay - self.get_npc_by_id(npc_id).arrival_delta
    
    def wait_for_npc(self) -> None:
        
        smallest_delta = min([self.arrival_delay - npc.arrival_delta for npc in self._npc_list])
        
        time.sleep(smallest_delta)
        time.sleep(1)
        
    
    def yield_npcs_by_arrival(self , handler : requests_handler) -> typing.Generator[DuelResultData, None, None]:
        while True:
            available_npcs_ids = [npc.duelnpc_id for npc in self._npc_list if self.is_ready(npc.duelnpc_id)]
            
            if len(available_npcs_ids) == 0:
                print('waiting for npc')
                self.wait_for_npc()
                self._reload_data(handler = handler)
                continue
                
            
            for npc_id in available_npcs_ids:
                yield npc_id
            
            self._reload_data(handler = handler)
        

def get_npc_duel_data(handler:requests_handler) -> NpcDuelList:
    
    reponse = handler.post(window='duel',action='get_data',use_h= True)
    
    if reponse['error'] :
        raise Exception('Something went wrong when loading the npc duel data!')
    
    motivation_npc = reponse['motivation_npc']
    npc_data = reponse['npcs']
    
    difficulty = npc_data['difficulty']
    npc_dict = npc_data['npcs']
    remaining_time = float(npc_data['remaining_time'])
    arrival_delay = npc_data['arrival_delay']
    
    return NpcDuelList(
        npc_duel_motivation = motivation_npc,
        difficulty = difficulty,
        npc_list = [DuelNpcData.load_from_dict(npc_data_dict=x) for x in npc_dict],
        remaining_time = remaining_time,
        arrival_delay = arrival_delay
    )

class NpcDuelManager():
    
    def __init__(self,
                 handler : requests_handler,
                 equipment_manager:Equipment_manager,
                 player_data : Player_data,
                 ):
        self.handler = handler
        self.equipment_manager = equipment_manager
        self.player_data = player_data
        
        self.npc_list = get_npc_duel_data(handler=self.handler)
        
        self.duel_equipment = None
        self.initial_equipment = self.equipment_manager.current_equipment
    
    def set_duel_equipment(self,duel_set : Equipment):
        
        self.duel_equipment = duel_set
    
    def duel_npc(self,npc_id : int):
        
        if self.duel_equipment is not None:
            
            self.equipment_manager.equip_equipment(equipment = self.duel_equipment,handler=self.handler)
        
        duel_result = self.npc_list.duel_npc(npc_id = npc_id,handler=self.handler)
        
        self.player_data.update_character_variables(handler=self.handler)
        
        if self.set_duel_equipment:
            self.equipment_manager.equip_equipment(equipment=self.initial_equipment,handler=self.handler)
        
        return duel_result
    
    def duel_smallest_aim_npc(self):
        
        smallest_aim_npc_id = self.npc_list.get_npc_by_smallest(key='aim')
        
        return self.duel_npc(npc_id=smallest_aim_npc_id)
    
    def duel_biggest_aim_npc(self):
        biggest_aim_npc_id = self.npc_list.get_npc_by_biggest(key='aim')
        
        return self.duel_npc(npc_id=biggest_aim_npc_id)
    
    @property
    def can_afford(self) -> bool:
        
        self.player_data.update_character_variables(handler=self.handler)
        
        return self.player_data.energy >= 5
    
    def reload(self):
        
        if self.npc_list.has_to_reload():
            
            self.npc_list._reload_data(handler= self.handler)
    
    def cycle_duels(self):
        
        for npc_id in self.npc_list.yield_npcs_by_arrival(handler=self.handler):
            
            if not self.can_afford:
                break
            
            yield self.duel_npc(npc_id=npc_id)