import typing

from automation_scripts.work_cycle import Script_work_task

from the_west_inner.requests_handler import requests_handler
from the_west_inner.game_classes import Game_classes
from the_west_inner.work_manager import Work_manager
from the_west_inner.player_data import Player_data
from the_west_inner.work import Work
from the_west_inner.consumable import Consumable_handler
from the_west_inner.reports import Reports_manager


from automation_scripts.sleep_func_callbacks.misc_func_callback import read_report_rewards,recharge_health
from automation_scripts.sleep_func_callbacks.callback_chain import CallbackChainer

class CycleJobsProducts():
    
    def __init__(self,
                 handler : requests_handler,
                 work_manager : Work_manager,
                 consumable_handler : Consumable_handler,
                 job_data : Work,
                 player_data : Player_data,
                 product_id : int,
                 game_classes : Game_classes
                 ):
        self.handler = handler
        self.work_manager = work_manager
        self.consumable_handler = consumable_handler
        self.job_data = job_data
        self.player_data = player_data
        self.product_id = product_id
        self.game_classes = game_classes
        self.report_manager = Reports_manager(handler=handler)
        self.work_callback_chainer = None
        self.consumable_callback_chainer = None
    
    
    def update_work_callback_chainer(self,callback_chain : CallbackChainer):
        self.work_callback_chainer = callback_chain
    
    def get_work_callback_function(self) -> typing.Callable | None:
        if self.work_callback_chainer is None:
            return None
        return self.work_callback_chainer.chain_function(report_manager = self.report_manager)
    
    def update_consumable_callback_chainer(self,callback_chain:CallbackChainer):
        self.consumable_callback_chainer = callback_chain
    
    def get_consumable_callback_function(self) -> typing.Callable | None:
        if self.consumable_callback_chainer is None:
            return None
        return self.consumable_callback_chainer.chain_function(report_manager = self.report_manager)
    
    def _recharge_energy(self,energy_consumable : int):
        self.consumable_handler.use_consumable(consumable_id = energy_consumable,
                                               function_callback = self.get_consumable_callback_function()
                                               )
        self.player_data.update_character_variables(handler=self.handler)
    
    def _recharge_by_actions(self,energy_consumable:int,actions : int):
        
        if actions < 0 :
            raise ValueError("Number of actions cannot be smaller than 0")
        
        if actions == 0:
            self._recharge_energy(energy_consumable=energy_consumable)
            return self.player_data.energy
        
        return actions
        
    def cycle_one_by_one(self,energy_consumable: int,target_number:int):
        
        dropped_items = 0
        possible_actions = self._recharge_by_actions(energy_consumable = energy_consumable,
                                                     actions = self.player_data.energy
                                                     )
        
                
        while dropped_items < target_number:
            
            work_task = Script_work_task(
                                        work_manager = self.work_manager,
                                        work_data = self.job_data,
                                        number_of_actions = 1,
                                        game_classes = self.game_classes
                                        )
            
            work_task.execute()
            possible_actions = self._recharge_by_actions(energy_consumable = energy_consumable,
                                                         actions = possible_actions - 1
                                                         )
            cycle_reward = self.report_manager._read_reports(retry_times=3)
            
            dropped_items = cycle_reward.item_drop.get(self.product_id,0)
            
        return self.report_manager.rewards
    def cycle(self,energy_consumable: int,target_number:int,number_of_task_groups : int = 9):
        
        dropped_items = 0
        possible_actions = self._recharge_by_actions(energy_consumable = energy_consumable,
                                                     actions = self.player_data.energy
                                                     )
        
        
        while dropped_items < target_number:
            tasks = min(number_of_task_groups,possible_actions)
            work_task = Script_work_task(
                                        work_manager = self.work_manager,
                                        work_data = self.job_data,
                                        number_of_actions = tasks,
                                        game_classes = self.game_classes
                                        )
            work_task.execute(callback_function=self.get_work_callback_function())
            possible_actions = self._recharge_by_actions(energy_consumable = energy_consumable,
                                                         actions = possible_actions - tasks
                                                         )
            
            self.report_manager._read_reports(retry_times=3)
            
            if dropped_items != self.report_manager.rewards.item_drop.get(self.product_id,0):
                print(f'we dropped {self.report_manager.rewards.item_drop.get(self.product_id,0) - dropped_items}')
            
            dropped_items = self.report_manager.rewards.item_drop.get(self.product_id,0)
            
            
            
        return self.report_manager.rewards