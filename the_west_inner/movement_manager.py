import typing

from towns import Town
from task_queue import TaskQueue
from work_manager import Work_manager
from misc_scripts import wait_until_date
from requests_handler import requests_handler
from player_data import Player_data
from map import Map


class MovementManager:
    
    def __init__(self ,
                 handler:requests_handler ,
                 task_queue : TaskQueue,
                 work_manager : Work_manager,
                 player_data : Player_data
                 ):
        
        self.handler = handler
        self.task_queue = task_queue
        self.work_manager = work_manager
        self.player_data = player_data
        self.map : Map = Map(handler = self.handler)
    def check_location(self,target_x : int , target_y : int) -> bool:
        return self.player_data.x == target_x and self.player_data.y == target_y
    def move_to_town(self,town:int|Town):
        if isinstance(town,Town):
            return self._move_to_town(town=town)
        elif isinstance(town,int) or isinstance(town,str):
            town = self.map.towns[town]
            return self._move_to_town(town = town)
    def _move_to_town(self,town : Town) -> int:
        if self.check_location(target_x = town.x , target_y=town.y):
            return town.town_id
        self.work_manager.move_to_town(town_id = town.town_id)
        wait_until_date(wait_time= self.task_queue.get_tasks_expiration(), handler = self.handler)
        self.player_data.update_location(handler = self.handler)
        return town.town_id
    def move_to_closest_town(self) :
        
        town_list = self.map.towns
        closest_town = town_list.get_closest_town(player_data = self.player_data)
        return self.move_to_town(town = closest_town)
