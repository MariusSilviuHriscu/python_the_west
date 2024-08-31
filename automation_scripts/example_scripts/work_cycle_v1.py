from the_west_inner.equipment import Equipment
from the_west_inner.login import Game_login
from the_west_inner.work import Work
from the_west_inner.work_manager import Work_manager

from automation_scripts.sleep_func_callbacks.callback_chain import CallbackChainer
from automation_scripts.sleep_func_callbacks.misc_func_callback import recharge_health_equipment
from automation_scripts.stop_events.script_events import StopEvent
from automation_scripts.stop_events.script_exception_handler import handle_exceptions
from automation_scripts.work_cycle import Cycle_jobs


def stop_works(work_manager : Work_manager):
    
    work_manager.cancel_all_tasks()

@handle_exceptions
def cycle_work(game_login : Game_login ,
               hp_equipment : Equipment,
               recharge_usable_list : list[int] ,
               job_data : list[Work],
               motivation_consumable : int ,
               energy_consumable : int,
               number_of_cycles : int = 1
               ):
    
    game = game_login.login()
    
    stop_work_chain = CallbackChainer()
    stop_work_chain.add_callback(
        callback_function=stop_works,
        work_manager = game.work_manager
    )
    
    
    
    chain = CallbackChainer()

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
    
    cycle = Cycle_jobs(
        game_classes= game,
        job_data = job_data,
        consumable_handler= game.consumable_handler
    )
    
    cycle.cycle(
        motivation_consumable=motivation_consumable,
        energy_consumable= energy_consumable,
        number_of_cycles= number_of_cycles
    )
    
    