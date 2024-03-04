from dataclasses import dataclass
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