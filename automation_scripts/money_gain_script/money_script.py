
import time
import typing
from automation_scripts.example_scripts.work_cycle_v1 import stop_works
from automation_scripts.sleep_func_callbacks.callback_chain import CallbackChainer
from automation_scripts.sleep_func_callbacks.misc_func_callback import recharge_health_equipment
from automation_scripts.work_cycle import Cycle_jobs
from the_west_inner.equipment import Equipment
from the_west_inner.game_classes import Game_classes
from the_west_inner.login import Game_login
from the_west_inner.misc_scripts import sleep_closest_town,collect_daily_reward
from the_west_inner.reports import Job_report_reward_data
from the_west_inner.work import Work, get_closest_workplace_data
from the_west_inner.work_job_data import WorkJobData
from typing import Protocol

from automation_scripts.pre_work_managers.pre_work_change_equip import PreWorkEquipChangerManager,EquipmentChangeCollection
from automation_scripts.pre_work_managers.pre_work_change_equip import PreWorkEquipChangerManager,PreWorkEquipChanger
from automation_scripts.pre_work_managers.mov_pre_work_managers import PreWorkMovementManager



class RepeatableScript(Protocol):
    
    def __init__(self ,
                 hp_equipment : Equipment | None = None,
                 mov_manager : PreWorkMovementManager | None = None,
                 pre_work_changer : PreWorkEquipChangerManager | None = None
                 ):
        self.hp_equipment = hp_equipment
        self.pre_work_changer = pre_work_changer
        self.mov_manager = mov_manager
    
    def can_run(self , game_classes : Game_classes) -> bool:
        pass
    
    
    def run(self , game_classes : Game_classes):
        pass
    
    def replace_pre_work_changer(self ,game_classes : Game_classes , pre_work_changer_table : dict):
        
        pass
    
    def replace_mov_manager(self , game_classes : Game_classes , mov_manager_table : dict):
        
        pass
    def replace_manager(self , game_classes : Game_classes):
        
        pass

class MoneyGainScript():
    
    def __init__(self ,
                 work_list : list[Work],
                 motivation_consumable : int,
                 recharge_usable_list : list[int],
                 hp_equipment : Equipment | None = None,
                 mov_manager : PreWorkMovementManager | None = None,
                 pre_work_changer : PreWorkEquipChangerManager | None = None
                 ):
        
        self.work_list = work_list
        self.motivation_consumable = motivation_consumable
        self.recharge_usable_list = recharge_usable_list
        
        self.hp_equipment = hp_equipment
        self.pre_work_changer = pre_work_changer
        self.mov_manager = mov_manager
    
    def can_run(self , game_classes : Game_classes) -> bool:
        
        return not game_classes.work_manager.task_queue.sleep_task_in_queue() or game_classes.player_data.energy == game_classes.player_data.energy_max
    
    
    def run(self , game_classes : Game_classes) -> Job_report_reward_data:
        
        cycle = Cycle_jobs(
            game_classes=game_classes,
            job_data=self.work_list,
            consumable_handler=game_classes.consumable_handler,
            clothes_changer_manager=self.pre_work_changer,
            mov_pre_work_manager=self.mov_manager
        )
        
        stop_work_chain = CallbackChainer()
        stop_work_chain.add_callback(
            callback_function=stop_works,
            work_manager = game_classes.work_manager
        )
        
        
        chain = CallbackChainer()

        chain.add_callback(
        callback_function=recharge_health_equipment,
        handler = game_classes.handler ,
        player_data = game_classes.player_data,
        work_manager = game_classes.work_manager,
        consumable_handler = game_classes.consumable_handler,
        recharge_hp_consumable_id = self.recharge_usable_list,
        equipment_manager = game_classes.equipment_manager,
        hp_equipment = self.hp_equipment,
        bag = game_classes.bag ,
        stop_event_callable = stop_work_chain.chain_function()
        )
        
        cycle.update_work_callback_chainer(callback_chain=chain)
        
        return cycle.cycle(
            motivation_consumable=self.motivation_consumable,
            energy_consumable=0,
            number_of_cycles=1
        )
    def replace_pre_work_changer(self ,game_classes : Game_classes ):
        
        self.pre_work_changer = PreWorkEquipChangerManager(
            work_equipment_table=self.pre_work_changer.work_equipment_table,
            handler=game_classes.handler,
            equipment_manager= game_classes.equipment_manager)
    
    def replace_mov_manager(self , game_classes : Game_classes ):
        
        self.mov_manager = PreWorkMovementManager(
            work_table= self.mov_manager.work_table,
            work_manager = game_classes.work_manager,
            movement_equipment = self.mov_manager.movement_equipment,
            equipment_manager= game_classes.equipment_manager,
            movement_manager= game_classes.movement_manager
            )
    def replace_manager(self , game_classes : Game_classes):
        
        self.replace_pre_work_changer(game_classes=game_classes)
        self.replace_mov_manager(game_classes=game_classes)
        

class RegenerationManager:
    
    
    def __init__(self , 
                 regeneration_equip : Equipment | None = None,
                 speed_equip : Equipment | None = None,
                 town_id : typing.Optional[int] = None,
                 callback : typing.Optional[typing.Callable[[],None]] = None
                 ):
        self.regeneration_equip = regeneration_equip
        self.speed_equip = speed_equip
        self.town_id = town_id
        self.callback = callback
    
    def sleep(self , game_classes : Game_classes):
        
        game_classes.work_manager.wait_until_free_queue(callback=self.callback)
        
        if self.speed_equip is not None:
            game_classes.equipment_manager.equip_equipment_concurrently(equipment=self.speed_equip,
                                                                        handler = game_classes.handler)
        
        if self.town_id is not None:
            game_classes.work_manager.sleep_task(room_type='luxurious_apartment',
                                                 town_id=self.town_id)
        else:
            sleep_closest_town(handler=game_classes.handler,player_data=game_classes.player_data)
        
        if self.regeneration_equip is not None:
            game_classes.equipment_manager.equip_equipment_concurrently(equipment=self.regeneration_equip,
                                                                        handler = game_classes.handler)
    
    def cancel_sleep(self , game_classes : Game_classes):
        
        game_classes.work_manager.cancel_all_tasks()

class MoneyScript:
    
    def __init__(self ,
                 login : Game_login,
                 regeneration_manager  : RegenerationManager,
                 repeatable_script : RepeatableScript                 
                 ):
        
        self.regeneration_manager = regeneration_manager
        self.repeatable_script = repeatable_script
        self.login = login
        
    
    def _run(self):
        
        game_classes = self.login.login()
        collect_daily_reward(handler = game_classes.handler)
        
        self.repeatable_script.replace_manager(game_classes=game_classes)
        
        if not self.repeatable_script.can_run(game_classes=game_classes):
            print('Cannot run')
            return
        print('Running')
        self.regeneration_manager.cancel_sleep(game_classes= game_classes)
        self.repeatable_script.run(game_classes= game_classes)
        
        print('Finished')
        self.regeneration_manager.sleep(game_classes= game_classes)
        print('Sleep')
    
    def run(self):
        while True:
            self._run()
            time.sleep(600)