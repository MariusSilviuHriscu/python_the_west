


import datetime
import time
import typing
from the_west_inner.bag import Bag
from the_west_inner.consumable import Consumable_handler
from the_west_inner.game_classes import Game_classes
from the_west_inner.login import Game_login
from the_west_inner.player_data import Player_data
from the_west_inner.requests_handler import requests_handler
from the_west_inner.work import Work
from the_west_inner.work_manager import Work_manager
from the_west_inner.misc_scripts import wait_until_date_callback


TIME_DICT = {
            1 : 1,
            600 : 6 ,
            3600 : 12
        }
class ContinuousTask:
    
    def __init__(self ,
                 handler : requests_handler ,
                 player_data : Player_data ,
                 work_manager : Work_manager,
                 consumable_manager : Consumable_handler,
                 bag : Bag,
                 work : Work,
                 work_number : int ,
                 usable_list : list[int]
                 ):
        self.handler = handler
        self.player_data = player_data
        self.work_manager = work_manager
        self.consumable_manager = consumable_manager
        self.bag = bag
        self.work = work
        self.work_number = work_number
        self.usable_list = usable_list
    
    def get_available_jobs(self , time_value : int) -> int:

        
        return min(
            self.player_data.energy // TIME_DICT.get(time_value),
             self.work_manager.allowed_tasks()
        ) if self.work_number == -1 else min(
            self.player_data.energy // TIME_DICT.get(time_value),
            self.work_manager.allowed_tasks(),
            self.work_number
        )
    
    def queue_tasks(self , work : Work , energy_usable : int) -> tuple[datetime.datetime | typing.Literal[-1] , int]:
        
        available_jobs = self.get_available_jobs(time_value = work.duration)
        if self.work_number != -1 and available_jobs > self.work_number:
            raise ValueError("The number of work tasks exceeds maximum!")
        if available_jobs == 0 and self.player_data.energy < TIME_DICT.get(work.duration):
            
            self.consumable_manager.use_consumable(consumable_id = energy_usable)
            self.player_data.update_all(handler = self.handler)
            
            return self.queue_tasks(work=work,
                                    energy_usable = energy_usable
                                    )
        
        if available_jobs == 0:
            
            return self.work_manager.task_queue.get_tasks_expiration(), available_jobs
        
        self.work_manager.work(
            work_object = work,
            number_of_tasks= available_jobs
        )
        return self.work_manager.task_queue.get_tasks_expiration() , available_jobs
    
    def dispatch_queue(self ) -> datetime.datetime:
        
        current_usable = next(iter([x for x in self.usable_list if self.bag[x] != 0]))
        
        if current_usable is None:
            raise ValueError('You do not have any usables to recharge your energy !')
        
        queue_result, used_tasks = self.queue_tasks(
                                        work= self.work,
                                        energy_usable = current_usable
                                        )
    
        if queue_result == -1:
            raise Exception('Something unexpected happened when queue-ing jobs ! ')
        
        if self.work_number != -1 :
            
            self.work_number -= used_tasks
        return queue_result
    def recharge_session_data(self, game :Game_classes):
        self.handler = game.handler
        self.player_data = game.player_data
        self.work_manager = game.work_manager
        self.consumable_manager = game.consumable_handler
        self.bag = game.bag
        

class ContinuousCycler:
    
    def __init__(self ,
                 login : Game_login ,
                 usable_list :list[int]
                 ):
        self.login = login
        self.usable_list = usable_list
    
    def create_task(self , 
                    work : Work ,
                    work_num : int,
                    game : Game_classes
                    ) -> ContinuousTask:
        
        return ContinuousTask(
            handler= game.handler,
            player_data= game.player_data,
            work_manager= game.work_manager,
            consumable_manager= game.consumable_handler,
            bag= game.bag,
            work= work,
            work_number=work_num,
            usable_list=self.usable_list
        )
    def sleep(self, end_time : datetime.datetime):
        print(f' End time is {end_time}')
        print(f' Start time is {datetime.datetime.now()}')
        
        wait_delta = end_time - datetime.datetime.now()
        wait_seconds = wait_delta.total_seconds()
        print(f'Wait time in {wait_seconds} seconds ')
        time.sleep(wait_seconds)
    def execute(self, work :Work , work_number : int):
        
        game = self.login.login()
        
            
        task = self.create_task(
            work= work,
            work_num= work_number,
            game= game
        )
        
        while task.work_number != 0:
            
            end = task.dispatch_queue()
            if task.work_number == 0:
                return
            self.sleep(end_time= end)
            game = self.login.login()
            task.recharge_session_data(game= game)
    