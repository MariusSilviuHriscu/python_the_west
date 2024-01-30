import time

from automation_scripts.work_cycle import Script_work_task

from the_west_inner.requests_handler import requests_handler
from the_west_inner.game_classes import Game_classes
from the_west_inner.work_manager import Work_manager
from the_west_inner.player_data import Player_data
from the_west_inner.work import Work
from the_west_inner.consumable import Consumable_handler
from the_west_inner.reports import Reports_manager


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
    
    def _recharge_energy(self,energy_consumable : int):
        self.consumable_handler.use_consumable(consumable_id = energy_consumable)
        self.player_data.update_character_variables(handler=self.handler)
    
    def _recharge_by_actions(self,energy_consumable:int,actions : int):
        
        if actions < 0 :
            raise ValueError("Number of actions cannot be smaller than 0")
        
        if actions == 0:
            self._recharge_energy(energy_consumable=energy_consumable)
            return self.player_data.energy
        
        return actions
        
    def cycle(self,energy_consumable: int,target_number:int):
        
        dropped_items = 0
        possible_actions = self._recharge_by_actions(energy_consumable = energy_consumable,
                                                     actions = self.player_data.energy
                                                     )
        
        
        
        report_manager = Reports_manager(handler=self.handler)
        
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
            cycle_reward = report_manager._read_reports(retry_times=3)
            
            dropped_items = cycle_reward.item_drop.get(self.product_id,0)
        return report_manager.rewards