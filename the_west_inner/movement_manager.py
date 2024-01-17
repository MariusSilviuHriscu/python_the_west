import typing

from player_data import Player_data
from towns import Town
from task_queue import TaskQueue
from work_manager import Work_manager
from misc_scripts import wait_until_date
from requests_handler import requests_handler
from player_data import Player_data
from map import Map

from game_classes import Game_classes

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
    def check_location(self,target_x : int , target_y : int) -> bool:
        return self.player_data.x,self.player_data.y == target_x,target_y
    def move_to_town(self,town : Town) -> int:
        if self.check_location(target_x=town.x,target_y=town.y):
            return town.town_id
        self.work_manager.move_to_town(town_id = town.town_id)
        wait_until_date(wait_time= self.task_queue.get_tasks_expiration(), handler = self.handler)
        self.player_data.update_location(handler = self.handler)
        return town.town_id
    def move_to_closest_town(self) :
        
        map = Map(handler = self.handler)
        town_list = map.towns
        closest_town = town_list.get_closest_town(player_data = self.player_data)
        return self.move_to_town(town = closest_town)
    @staticmethod
    def load_from_game_classes(game_data:Game_classes) -> typing.Self:
        
        return MovementManager(
                                handler = game_data.handler,
                                task_queue = game_data.task_queue,
                                work_manager = game_data.work_manager,
                                player_data = game_data.player_data
                                )