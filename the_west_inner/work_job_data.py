import typing
from typing import Protocol
from dataclasses import dataclass

from requests_handler import requests_handler
from player_data import Player_data
from map import Map

@dataclass
class WorkData:
    cost : int
    money : int
    xp : int
    luck : int
    duration : int
    product_id_list : list[int]
    
    
@dataclass
class JobDataDamage:
    damage_probability : int
    damage_max_damage : int
    
    def average_damage(self , max_hp : int) ->int:
        return self.damage_max_damage * self.damage_probability * max_hp
class WorkJobData:
    def __init__(self,
                 work_id : int ,
                 skill_points_required : int,
                 work_points : int,
                 motivation : int,
                 item_drop_interval : tuple[int,int] ,
                 stage : int ,
                 malus : int ,
                 timed_work_data : dict[typing.Literal[15,600,3600] : WorkData]
                ):

        self.work_id = work_id
        self.skill_points_required = skill_points_required
        self.work_points = work_points
        self.motivation = motivation
        self.item_drop_interval = item_drop_interval
        self.stage = stage
        self.malus = malus
        self.timed_work_data = timed_work_data

        self._job_data_damage = None
        self._job_data = None
        
    def _load_job_data(self , handler : requests_handler , x : int, y : int) -> None :
        
        payload = {
            'jobId' : self.work_id,
            'x' : x,
            'y' : y
        }
        
        response = handler.post(window='job',action='job',action_name='mode',payload=payload)
        
        
        self._job_data = response
            
        return response
    
    @property
    def job_data(self) -> dict:
        
        return self._job_data
    
    def job_data_damage(self) -> JobDataDamage:
        return self._job_data_damage
    
    def load_joab_damage(self, handler : requests_handler , x : int , y : int) -> JobDataDamage:
        
        if self.job_data is None:
            
            self._load_job_data(
                handler= handler,
                x = x ,
                y = y)
        
        job_damage = JobDataDamage(
            damage_probability = self.job_data.get('danger'),
            damage_max_damage= self.job_data.get('maxdmg')
        )
        
        self._job_data_damage = job_damage
        
        return job_damage

class WorkDataLoader():
    def __init__(self, handler : requests_handler ):
        self.handler = handler
    def _load_work_data(self , work_data : dict) -> WorkData:
        return WorkData(
            cost = work_data.get('cost'),
            money = work_data.get('money'),
            xp = work_data.get('xp'),
            luck = work_data.get('luck'),
            duration = work_data.get('duration'),
            product_id_list = [x.get('itemid',None) for x in work_data.get('items') if x.get('itemid',None) is not None]
        )
    def _load_work_info(self , job_id : int|str , job_dict: dict) -> WorkJobData:
        work_time_info = job_dict.get('durations')
        return WorkJobData(
            work_id = int(job_id),
            skill_points_required = job_dict.get('jobSkillPoints'),
            work_points = job_dict.get('workpoints'),
            motivation = job_dict.get('motivation'),
            item_drop_interval = (job_dict.get('minMaxItemVal')[0] , job_dict.get('minMaxItemVal')[1]),
            stage = job_dict.get('stage').get('stage'),
            malus= job_dict.get('stage').get('malus'),
            timed_work_data = {x.get('duration') : self._load_work_data(work_data = x) 
                                                    for x in work_time_info}
        )
        
    def get_work_info(self,handler:requests_handler) -> list[WorkJobData]:
        
        response = handler.post(window="work", action="index", action_name="mode")['jobs']
        
        return [self._load_work_info(job_id = job_id,
                                     job_dict = job_dict
                                     ) for job_id,job_dict in response.items()]
class WorkSortRule(Protocol):
    def __init__(self) -> None:
        pass
    
    def value(self,work_data : WorkJobData) -> int:
        pass
class WorkValidationRule(Protocol):
    def __init__(self) -> None:
        pass
    
    def validate(self,work_data : WorkJobData) -> bool:
        pass

class DamageValidationRule():
    def __init__(self,
                 handler:requests_handler,
                 player_data : Player_data,
                 map : Map ,
                 max_allowed_damage_percent: float):
        self.handler = handler
        self.player_data = player_data
        self.map = map
        self.max_allowed_damage_percent = max_allowed_damage_percent
    def _max_damage(self) ->int:
        
        return int(self.player_data.hp_max * self.max_allowed_damage_percent)
    def validate(self,work_data : WorkJobData) -> bool:
        
        work_map_obj = self.map.job_location_data.get_random_job(job_id = work_data.work_id)
        
        work_data.load_joab_damage(handler=self.handler,
                                   x = work_map_obj.job_x,
                                   y = work_map_obj.job_y
                                   )
        return work_data.job_data_damage().average_damage(max_hp = self.player_data.hp_max) < self._max_damage()
class ExpDamageRule():
    
    def __init__(self, time_value : typing.Literal[15,60,3600]):
        self.time_value = time_value
    
    def value(self , work_data : WorkJobData):
        
        work : WorkData = work_data.timed_work_data[self.time_value]
        return work.xp
class WorkJobDataManager:
    
    def __init__(self , 
                 player_data : Player_data ,
                 work_job_data_list : list[WorkJobData] ,
                 map : Map
                 ) :
        self.player_data = player_data
        self.map = map
        self.work_job_data_list = work_job_data_list
        
        self.work_dict = {x.work_id : x for x in work_job_data_list}
    
    def sort_by_work_sort_rule(self, work_sort_rule : WorkSortRule,filter_rule : WorkValidationRule|None):
        
        return sorted(
            [x for x in self.work_job_data_list if filter_rule.validate(work_data = x)],
            key = work_sort_rule.value ,
            reverse= True
            )