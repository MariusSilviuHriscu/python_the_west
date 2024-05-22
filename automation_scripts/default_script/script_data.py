from dataclasses import dataclass
import pathlib
import json

from the_west_inner.equipment import Equipment

@dataclass
class Script_settings:
    name : str
    password : str
    world_id : str
    target_product_id : int
    target_desired_job_id : int
    motivation_consumable : int
    energy_consumable : int
    luck_bonus_consumable : int
    product_equipment : Equipment
    work_equipment : Equipment
    work_flag :bool
    load_script_tag : bool

def create_equipment_from_dict(equipment_dict:dict)  ->Equipment:
    return Equipment(
                    head_item_id= equipment_dict['head_item_id'] ,
                    neck_item_id= equipment_dict['neck_item_id'] ,
                    left_arm_item_id= equipment_dict['left_arm_item_id'] ,
                    body_item_id= equipment_dict['body_item_id'] ,
                    right_arm_item_id= equipment_dict['right_arm_item_id'] ,
                    foot_item_id= equipment_dict['foot_item_id'] ,
                    animal_item_id= equipment_dict['animal_item_id'] ,
                    belt_item_id= equipment_dict['belt_item_id'] ,
                    pants_item_id= equipment_dict['pants_item_id'] ,
                    yield_item_id= equipment_dict['yield_item_id'] 
                    )

def create_script_settings_from_dict(username:str,passworld:str,settings_dict:dict) -> Script_settings:
    product_equipment,work_equipment = None, None
    if settings_dict['seconds_flag'] :
        product_equipment = create_equipment_from_dict( equipment_dict= settings_dict.get("product_equipment"))
        work_equipment = create_equipment_from_dict( equipment_dict = settings_dict["work_equipment"])
    
        
    return Script_settings(
        name = username,
        password = passworld,
        world_id= settings_dict.get('world_id'),
        target_product_id = settings_dict.get('target_product_id'),
        target_desired_job_id = settings_dict.get('target_desired_job_id'),
        motivation_consumable = settings_dict.get('motivation_consumable'),
        energy_consumable = settings_dict.get('energy_consumable'),
        luck_bonus_consumable = settings_dict.get('luck_bonus_consumable'),
        product_equipment = product_equipment,
        work_equipment = work_equipment,
        work_flag = settings_dict.get('seconds_flag') == "True",
        load_script_tag = settings_dict.get('load_script_tag','True') == 'True'
    )

def load_settings_dict(setting_file_name:str , path: pathlib.Path =None) -> list[Script_settings]:
    if path is None:
        path = pathlib.Path.cwd()
    path = path/setting_file_name
    
    script_settings_list = []
    
    with open(path) as json_file:
        accounts_dict = json.load(json_file)
        for account_dict in accounts_dict:
            for world_dict in account_dict['worlds']:
                script_settings_list.append(
                                            create_script_settings_from_dict(
                                                                            username = account_dict['name'],
                                                                            passworld = account_dict['password'],
                                                                            settings_dict = world_dict
                                                                            )
                                            )
        return script_settings_list