from the_west_inner.requests_handler import requests_handler
from the_west_inner.reports import Reports_manager
from the_west_inner.player_data import Player_data
from the_west_inner.consumable import Consumable_handler
from the_west_inner.work_manager import Work_manager



def read_report_rewards(report_manager : Reports_manager):
    report_manager._read_reports(retry_times=3)
    print(f'i have read this : {report_manager.rewards}')

def recharge_health(handler: requests_handler ,
                    player_data : Player_data ,
                    work_manager : Work_manager ,
                    consumable_handler : Consumable_handler ,
                    recharge_hp_consumable_id : int ):
    
    player_data.update_character_variables(handler=handler)
    
    print('checked hp')
    if player_data.hp / player_data.hp_max < 0.25 :
        
        work_manager.cancel_all_tasks()
        consumable_handler.use_consumable(consumable_id = recharge_hp_consumable_id)
        
        player_data.update_character_variables(handler=handler)