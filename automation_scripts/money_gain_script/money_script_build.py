from automation_scripts.money_gain_script.money_script import MoneyGainScript,MoneyScript,RegenerationManager
from automation_scripts.pre_work_managers.mov_pre_work_loader import PreWorkMovManagerBuilder
from automation_scripts.pre_work_managers.mov_pre_work_managers import PreWorkMovementManager
from automation_scripts.pre_work_managers.pre_work_change_equip import EquipmentChangeCollection, PreWorkEquipChangerManager
from the_west_inner.equipment import Equipment, SavedEquipmentManager
from the_west_inner.game_classes import Game_classes
from the_west_inner.login import Game_login
from the_west_inner.work import Work, get_closest_workplace_data



def make_job_list(work_id_list : list[int] , game_classes : Game_classes) -> list[Work]:
    job_data = []
    for work_id in work_id_list:
        job_id , x ,y = get_closest_workplace_data(
        handler= game_classes.handler,
        job_id= work_id,
        job_list = game_classes.work_list,
        player_data= game_classes.player_data
        )
        job_data.append(Work(job_id=job_id,x=x,y=y,duration=15))
    return job_data


def make_money_gain_script(
                login : Game_login,
                work_id_list : list[int],
                hp_equipment : Equipment,
                regeneration_equip : Equipment,
                motivation_consumable : int,
                recharge_usable_list : list[int],
                town_id : int | None = None,
                movement_equipment : None | Equipment = None,
                work_eq_dict : dict[int,EquipmentChangeCollection] | None = None
                ) -> MoneyScript:
    
    game = login.login()
    
    regeneration_manager = RegenerationManager(
        regeneration_equip = regeneration_equip,
        speed_equip= movement_equipment,
        town_id = town_id
    )
    
    job_data = make_job_list(work_id_list=work_id_list , game_classes=game)
    
    if movement_equipment is not None :
        pre_work_movement_manager_builder = PreWorkMovManagerBuilder(game_classes=game)
        pre_work_movement_manager = pre_work_movement_manager_builder.build(
            work_list=job_data,
            movement_equipment = movement_equipment
        )
    else:
        pre_work_movement_manager = None
    
    if work_eq_dict is not None :
        
        saved_equipment_manager = SavedEquipmentManager(
            handler = game.handler,
            bag= game.bag
        )
        
        
        for job_work_equipment in work_eq_dict.values():
            if not job_work_equipment.loaded :
                job_work_equipment.load(saved_equip_manager=saved_equipment_manager)
            
    
        pre_work_change_manager = PreWorkEquipChangerManager(
                                        work_equipment_table = work_eq_dict,
                                        handler = game.handler,
                                        equipment_manager= game.equipment_manager
                                        )
    
    money_gain_script = MoneyGainScript(
        work_list = job_data,
        motivation_consumable= motivation_consumable,
        recharge_usable_list= recharge_usable_list,
        hp_equipment= hp_equipment,
        mov_manager= pre_work_movement_manager,
        pre_work_changer= pre_work_change_manager
        
    )
    
    return MoneyScript(
        game_classes = game,
        regeneration_manager= regeneration_manager,
        repeatable_script= money_gain_script
    )