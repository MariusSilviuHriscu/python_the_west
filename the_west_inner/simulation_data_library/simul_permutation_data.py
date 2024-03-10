from dataclasses import dataclass

from the_west_inner.requests_handler import requests_handler
from the_west_inner.equipment import Equipment,Equipment_manager

from the_west_inner.simulation_data_library.simul_items import Weapon_damage_range
from the_west_inner.simulation_data_library.simul_skills import Skills


@dataclass
class EquipmentPermutationData:
    item_drop : int
    exp_bonus : int
    workpoints : int
    weapon_damage : Weapon_damage_range
    product_drop : int
    regeneration : int
    status : Skills
    permutation : dict
    
    
    def equip(self,handler:requests_handler , equipment_manager : Equipment_manager):
        get_id = lambda x , y : x.get(y,None).item_id if x.get(y,None) else None
        equipment = Equipment(
            head_item_id = get_id(self.permutation,'headgear'),
            neck_item_id= get_id(self.permutation,'necklace'),
            left_arm_item_id= get_id(self.permutation,'fort_weapon'),
            body_item_id= get_id(self.permutation,'clothes' ),
            right_arm_item_id= get_id(self.permutation,'weapon'),
            foot_item_id=get_id(self.permutation,'boots'),
            animal_item_id=get_id(self.permutation,'animal'),
            belt_item_id=get_id(self.permutation,'belt'),
            pants_item_id=get_id(self.permutation,'pants'),
            yield_item_id=get_id(self.permutation,'produs')
        )
        print(equipment)
        equipment_manager.equip_equipment(equipment = equipment , handler = handler)