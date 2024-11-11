


import datetime
import typing
from the_west_inner.bag import Bag
from the_west_inner.consumable import Consumable_handler
from the_west_inner.game_classes import Game_classes
from the_west_inner.player_data import Player_data
from the_west_inner.work import Work
from the_west_inner.work_manager import Work_manager

TIME_DICT = {
            1 : 1,
            60 : 6 ,
            3600 : 12
        }
class ContinuousJobsCycling():
    
    def __init__(self ,
                 player_data : Player_data ,
                 work_manager : Work_manager,
                 consumable_manager : Consumable_handler,
                 bag : Bag,
                 usable_list : list[int]
                 ):
        self.player_data = player_data
        self.work_manager = work_manager
        self.consumable_manager = consumable_manager
        self.bag = bag
        self.usable_list = usable_list
    
    def get_available_jobs(self , time_value : int) -> int:

        
        return min(
            self.player_data.energy // TIME_DICT.get(time_value),
             self.work_manager.allowed_tasks()
        )
    
    def queue_tasks(self , work : Work , energy_usable : int) -> datetime.datetime | typing.Literal[-1]:
        
        available_jobs = self.get_available_jobs(time_value = work.duration)
        
        if available_jobs == 0 and self.player_data.energy < TIME_DICT.get(work.duration):
            
            self.consumable_manager.use_consumable(consumable_id = energy_usable)
            
            return self.queue_tasks(work=work,
                                    energy_usable = energy_usable
                                    )
        
        if available_jobs == 0:
            
            return self.work_manager.task_queue.get_tasks_expiration()
        
        self.work_manager.work(
            work_object = work,
            number_of_tasks= available_jobs
        )
        return self.work_manager.task_queue.get_tasks_expiration()
    
    def dispatch_queue(self , work : Work) :
        
        current_usable = next(iter([x for x in self.usable_list if self.bag[x] != 0]))
        
        if current_usable is None:
            raise ValueError('You do not have any usables to recharge your energy !')
        
        queue_result = self.queue_tasks(work= work,
                                        energy_usable = current_usable
                                        )
        
        if queue_result == -1:
            raise Exception('Something unexpected happened when queue-ing jobs ! ')
        
        
        