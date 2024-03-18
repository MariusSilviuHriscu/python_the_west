import typing
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