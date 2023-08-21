from dataclasses import dataclass
import pathlib
import json

from ...the_west_inner.equipment import Equipment

@dataclass
class Script_settings:
    """
    Data class representing the settings for the script.

    Attributes:
        name (str): The player's name.
        password (str): The player's password.
        world_id (str): The ID of the world.
        target_product_id (int): The ID of the target product.
        target_desired_job_id (int): The ID of the desired job.
        motivation_consumable (int): The ID of the motivation consumable.
        energy_consumable (int): The ID of the energy consumable.
        luck_bonus_consumable (int): The ID of the luck bonus consumable.
        product_equipment (Equipment): Equipment for product actions.
        work_equipment (Equipment): Equipment for work actions.
        work_flag (bool): Flag indicating whether to perform work actions.
    """

def create_equipment_from_dict(equipment_dict: dict) -> Equipment:
    """
    Create an Equipment instance from a dictionary.

    Args:
        equipment_dict (dict): Dictionary containing equipment data.

    Returns:
        Equipment: An Equipment instance.
    """
    return Equipment(
        head_item_id=equipment_dict['head_item_id'],
        neck_item_id=equipment_dict['neck_item_id'],
        left_arm_item_id=equipment_dict['left_arm_item_id'],
        body_item_id=equipment_dict['body_item_id'],
        right_arm_item_id=equipment_dict['right_arm_item_id'],
        foot_item_id=equipment_dict['foot_item_id'],
        animal_item_id=equipment_dict['animal_item_id'],
        belt_item_id=equipment_dict['belt_item_id'],
        pants_item_id=equipment_dict['pants_item_id'],
        yield_item_id=equipment_dict['yield_item_id']
    )

def create_script_settings_from_dict(username: str, password: str, settings_dict: dict) -> Script_settings:
    """
    Create a Script_settings instance from a dictionary.

    Args:
        username (str): The player's username.
        password (str): The player's password.
        settings_dict (dict): Dictionary containing script settings.

    Returns:
        Script_settings: A Script_settings instance.
    """
    product_equipment, work_equipment = None, None
    if settings_dict['seconds_flag']:
        product_equipment = create_equipment_from_dict(equipment_dict=settings_dict.get("product_equipment"))
        work_equipment = create_equipment_from_dict(equipment_dict=settings_dict["work_equipment"])

    return Script_settings(
        name=username,
        password=password,
        world_id=settings_dict.get('world_id'),
        target_product_id=settings_dict.get('target_product_id'),
        target_desired_job_id=settings_dict.get('target_desired_job_id'),
        motivation_consumable=settings_dict.get('motivation_consumable'),
        energy_consumable=settings_dict.get('energy_consumable'),
        luck_bonus_consumable=settings_dict.get('luck_bonus_consumable'),
        product_equipment=product_equipment,
        work_equipment=work_equipment,
        work_flag=settings_dict.get('seconds_flag') == "True"
    )

def load_settings_dict(setting_file_name: str, path: pathlib.Path = None) -> list[Script_settings]:
    """
    Load script settings from a JSON file.

    Args:
        setting_file_name (str): The name of the settings JSON file.
        path (pathlib.Path): Optional path to the JSON file.

    Returns:
        list[Script_settings]: A list of Script_settings instances.
    """
    if path is None:
        path = pathlib.Path.cwd()
    path = path / setting_file_name

    script_settings_list = []

    with open(path) as json_file:
        accounts_dict = json.load(json_file)
        for account_dict in accounts_dict:
            for world_dict in account_dict['worlds']:
                script_settings_list.append(
                    create_script_settings_from_dict(
                        username=account_dict['name'],
                        password=account_dict['password'],
                        settings_dict=world_dict
                    )
                )
    return script_settings_list