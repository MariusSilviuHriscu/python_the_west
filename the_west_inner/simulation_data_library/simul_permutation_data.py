from dataclasses import dataclass

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
    
    
    def equip(self):
        
        equipment = Equipment(
            head_item_id = 0,
            neck_item_id= 0,
            left_arm_item_id= 0,
            body_item_id= 0 ,
            right_arm_item_id= 0,
            foot_item_id=0,
            animal_item_id=0,
            belt_item_id=0,
            pants_item_id=0,
            yield_item_id=0
        )