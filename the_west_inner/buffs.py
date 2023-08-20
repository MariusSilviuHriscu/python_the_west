import typing
import datetime
from dataclasses import dataclass
import warnings
from time import ctime

from misc_scripts import server_time
from requests_handler import requests_handler

@dataclass
class Buff_data:
    buff_id : int
    buff_type : str 
    buff_time: datetime.datetime
    description : list[str]
    duration : int|None = None
    charge : int|None = None
    def has_finished(self,handler:requests_handler):
        return server_time(handler = handler) > self.buff_time

@dataclass
class Character_buff:
    buff_data : Buff_data
    attributes : list|dict[str:int] 
    skills : list|dict[str:int] 
    luck_bonus : float = 0
    def is_buff(self,buff_id:int):
        return self.buff_data.buff_id == buff_id
    def has_finished(self,handler:requests_handler):
        return self.buff_data.has_finished(handler = handler)
    
@dataclass
class Travel_buff:
    buff_data : Buff_data
    speed : float
    def is_buff(self,buff_id:int):
        return self.buff_data.buff_id == buff_id
    def has_finished(self,handler:requests_handler):
        return self.buff_data.has_finished(handler = handler)


@dataclass
class Item_buff:
    buff_data : Buff_data
    weapon_hand : typing.Literal["left_hand","right_hand"]
    fort_battle : list | dict[str,int] 
    min_damage : int = 0
    max_damage : int = 0
    lvl_damage : int = 0
    health : int = 0
    lvl_health : int = 0
    def is_buff(self,buff_id:int):
        return self.buff_data.buff_id == buff_id
    def has_finished(self,handler:requests_handler):
        return self.buff_data.has_finished(handler = handler)




class Buff_list():
    def __init__(self):
        self.buff_list:list[Item_buff|Travel_buff|Character_buff] = []
    
    
    def add(self,buff:Character_buff|Travel_buff|Item_buff) :
        self.buff_list.append(buff)
    
    def __contains__(self,buff_id:int):
        for buff in self.buff_list:
            if buff.is_buff(buff_id):
                return True
        return False
    def get_by_id(self,buff_id) -> None|Character_buff|Travel_buff|Item_buff:
        
        if buff_id not in self:
            return None
        
        for buff in self.buff_list:
            if buff.is_buff(buff_id):
                return buff
        
        raise Exception(f"Getting the buf by id has not worked properly : {buff_id}")
    def get_by_type(self,desired_buff_type:typing.Type[Character_buff|Travel_buff|Item_buff]|str):
        if isinstance(desired_buff_type,str):
            for buff in self.buff_list:
                if buff.buff_data.buff_type == desired_buff_type:
                    return buff
        for buff in self.buff_list:
            if isinstance(buff,desired_buff_type):
                return buff
        return None

def build_buff_by_dict(input_dict:dict) -> Buff_data:
    if "buff_id" not in input_dict:
        raise Exception("Could not find any buff_id,something is incorrect about input_dict")
    buff_id = input_dict['buff_id']
    buff_type = input_dict['type']
    buff_time = datetime.timedelta(seconds=input_dict['time']) + datetime.datetime.now()
    description = input_dict['description']
    duration = input_dict['duration']
    charge = input_dict['charge']
    
    return Buff_data(
                    buff_id = buff_id,
                    buff_type = buff_type,
                    buff_time = buff_time,
                    description = description,
                    duration = duration,
                    charge = charge
                    )
def build_character_buff(input_dict) -> Character_buff:
    return Character_buff(
                        buff_data = build_buff_by_dict(input_dict= input_dict),
                        attributes = input_dict['attributes'],
                        skills = input_dict['skills'],
                        luck_bonus = input_dict['luckbonus']
                        )
def build_travel_buff(input_dict):
    return Travel_buff(
                        buff_data = build_buff_by_dict(input_dict=input_dict),
                        speed = input_dict['speed']
                        )
def build_item_buff(input_dict):
    return Item_buff(
                    buff_data = build_buff_by_dict(input_dict=input_dict),
                    weapon_hand = input_dict['weapon_hand'],
                    min_damage = input_dict['min_damage'],
                    max_damage= input_dict['max_damage'],
                    lvl_damage = input_dict['lvl_damage'],
                    health = input_dict['health'],
                    lvl_health = input_dict['lvl_health'],
                    fort_battle = input_dict['fortbattle']
                    )
def build_buff_list(input_dict) -> Buff_list:
    buff_list = Buff_list()
    mapping_function_dict ={
                            'character' : build_character_buff,
                            'travel' : build_travel_buff,
                            'items' : build_item_buff
                            }
    for buff_type,buff_dict in input_dict.items():
        if buff_dict is None :
            continue
        if buff_type not in mapping_function_dict:
            print(buff_type,buff_dict)
            warnings.warn(f"Unknown type of buff : {buff_type}")
            continue
        buff_list.add(
                        buff = mapping_function_dict[buff_type](buff_dict) 
                      )
    return buff_list