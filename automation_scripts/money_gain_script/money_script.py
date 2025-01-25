
from datetime import time
import typing
from the_west_inner.equipment import Equipment
from the_west_inner.game_classes import Game_classes
from the_west_inner.login import Game_login
from the_west_inner.misc_scripts import sleep_closest_town
from the_west_inner.work_job_data import WorkJobData
from typing import Protocol

from automation_scripts.pre_work_managers.pre_work_change_equip import PreWorkEquipChangerManager,EquipmentChangeCollection


class RepeatableScript(Protocol):
    
    def __init__(self ,
                 speed_equip : Equipment | None = None,
                 work_eq_dict : dict[int,EquipmentChangeCollection] | None = None
                 ):
        
        self.work_eq_dict = work_eq_dict
        self.speed_equip = speed_equip
    
    def can_run(self , game_classes : Game_classes) -> bool:
        pass
    
    
    def run(self , game_classes : Game_classes):
        pass

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
        
        self._game_classes = None
    
    @property
    def game_classes(self) -> Game_classes:
        if self._game_classes is None:
            self._game_classes = self.login.login()
        return self._game_classes
    
    def delete_game_classes(self):
        self._game_classes = None
    
    def _run(self):
        
        if not self.repeatable_script.can_run(game_classes=self.game_classes):
            print('Cannot run')
            return
        print('Running')
        self.regeneration_manager.cancel_sleep(game_classes=self.game_classes)
        self.repeatable_script.run(game_classes=self.game_classes)
        
        print('Finished')
        self.regeneration_manager.sleep(game_classes=self.game_classes)
        print('Sleep')
    
    def run(self):
        while True:
            self._run()
            time.sleep(600)