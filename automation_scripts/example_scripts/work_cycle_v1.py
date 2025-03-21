import datetime
from automation_scripts.pre_work_managers.mov_pre_work_managers import PreWorkMovementManager
from automation_scripts.pre_work_managers.pre_work_change_equip import PreWorkEquipChangerManager,EquipmentChangeCollection
from the_west_inner.equipment import Equipment,SavedEquipmentManager
from the_west_inner.login import Game_login
from the_west_inner.work import Work
from the_west_inner.work_manager import Work_manager

from automation_scripts.sleep_func_callbacks.callback_chain import CallbackChainer
from automation_scripts.sleep_func_callbacks.misc_func_callback import recharge_health_equipment
from automation_scripts.stop_events.script_events import StopEvent
from automation_scripts.stop_events.script_exception_handler import handle_exceptions
from automation_scripts.work_cycle import Cycle_jobs
from automation_scripts.pre_work_managers.mov_pre_work_loader import PreWorkMovManagerBuilder
from automation_scripts.sleep_func_callbacks.universal_callback_map import UNIVERSAL_MAPPING

def stop_works(work_manager : Work_manager):
    
    work_manager.cancel_all_tasks()


class ScriptTimer:
    
    def __init__(self , time_data : None | datetime.timedelta | datetime.datetime):
        
        self.creation_date = datetime.datetime.now()
        
        self.end_time = time_data + self.creation_date if isinstance(time_data , datetime.timedelta) else time_data
        print(self.end_time)
        
        self.stop_event = StopEvent()
    def is_time_over(self) -> bool:
        
        if self.end_time is None:
            return False
        
        return datetime.datetime.now() > self.end_time
    
    def check(self):
        print(self.is_time_over())
        if not self.is_time_over():
            return
        
        self.stop_event.raise_exception()


@handle_exceptions
def cycle_work(game_login : Game_login ,
               hp_equipment : Equipment,
               recharge_usable_list : list[int] ,
               job_data : list[Work],
               motivation_consumable : int ,
               energy_consumable : int,
               number_of_cycles : int = 1,
               time_data : None | datetime.timedelta | datetime.datetime = None,
               pre_work_change_manager : None | PreWorkEquipChangerManager = None,
               pre_work_movement_manager : None | PreWorkMovementManager = None,
               movement_equipment : None | Equipment = None,
               work_eq_dict : dict[int,EquipmentChangeCollection] | None = None,
               additional_chainer : None | CallbackChainer = None
               ):
    
    game = game_login.login()
    
    stop_work_chain = CallbackChainer()
    stop_work_chain.add_callback(
        callback_function=stop_works,
        work_manager = game.work_manager
    )
    
    
    chain = CallbackChainer(UNIVERSAL_MAPPING)

    chain.add_callback(
    callback_function=recharge_health_equipment,
    handler = game.handler ,
    player_data = game.player_data,
    work_manager = game.work_manager,
    consumable_handler = game.consumable_handler,
    recharge_hp_consumable_id = recharge_usable_list,
    equipment_manager = game.equipment_manager,
    hp_equipment = hp_equipment,
    bag = game.bag ,
    stop_event_callable = stop_work_chain.chain_function()
    )
    
    timer = ScriptTimer(time_data=time_data)
    
    
    chain.add_callback(
        callback_function = timer.check
    )
    
    if additional_chainer is not None:
        new_func = additional_chainer.chain_function(game_classes=game)
        chain.add_callback(
            callback_function=new_func
        )
    if movement_equipment is not None and pre_work_movement_manager is None:
        pre_work_movement_manager_builder = PreWorkMovManagerBuilder(game_classes=game)
        pre_work_movement_manager = pre_work_movement_manager_builder.build(
            work_list=job_data,
            movement_equipment = movement_equipment
        )
    
    if work_eq_dict is not None :
        
        saved_equipment_manager = SavedEquipmentManager(
            handler = game.handler,
            bag= game.bag
        )
        
        
        for job_work_equipment in work_eq_dict.values():
            if not job_work_equipment.loaded :
                job_work_equipment.load(saved_equip_manager=saved_equipment_manager)
            
    
    if work_eq_dict is not None and pre_work_change_manager is None:
        pre_work_change_manager = PreWorkEquipChangerManager(
                                        work_equipment_table = work_eq_dict,
                                        handler = game.handler,
                                        equipment_manager= game.equipment_manager
                                        )

    
    cycle = Cycle_jobs(
        game_classes= game,
        job_data = job_data,
        consumable_handler= game.consumable_handler,
        clothes_changer_manager = pre_work_change_manager,
        mov_pre_work_manager = pre_work_movement_manager
    )
    
    cycle.update_work_callback_chainer(
        callback_chain= chain
    )
    try :
        cycle.cycle(
            motivation_consumable=motivation_consumable,
            energy_consumable= energy_consumable,
            number_of_cycles= number_of_cycles
        )
    except Exception as e:
        
        print(cycle.reports_manager.rewards)
        raise e