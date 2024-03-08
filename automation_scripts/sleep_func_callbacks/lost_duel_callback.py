from the_west_inner.bag import Bag
from the_west_inner.requests_handler import requests_handler
from the_west_inner.game_classes import Game_classes
from the_west_inner.items import Items
from the_west_inner.equipment import Equipment_manager,Equipment
from the_west_inner.item_set_general import get_item_sets,Item_sets
from the_west_inner.player_data import Player_data

from the_west_inner.item_set_general import get_item_sets,Item_sets
from the_west_inner.simulation_data_library.load_items_script import get_simul_items,get_simul_sets
from the_west_inner.simulation_data_library.simul_sets import create_set_instance_list,Item_set_list
from the_west_inner.simulation_data_library.simul_equipment import _game_data_to_current_equipment
from the_west_inner.simulation_data_library.calc_maxim import Brute_force_simulation_bonus_check
from the_west_inner.simulation_data_library.simul_items import Item_list,create_item_list_from_model,Item_model_list,Weapon_damage_range
from the_west_inner.simulation_data_library.load_items_script import get_simul_items,get_simul_sets
from the_west_inner.simulation_data_library.simul_sets import create_set_instance_list,Item_set_list
from the_west_inner.simulation_data_library.simul_equipment import create_simul_equipment_by_current_equipment
from the_west_inner.simulation_data_library.simul_equip_fitnes import SimulFitnessRuleSet
from the_west_inner.simulation_data_library.simul_equip_rules.weapon_damage_rule import WeaponDamageSimulRule
from the_west_inner.simulation_data_library.simul_equip_rules.total_skill_points_rule import TotalSkillPointsRule
from the_west_inner.simulation_data_library.calc_maxim import Simulation_data_loader

def low_level_npc_duel_loss_callback(
    game_classes : Game_classes
    ) -> None:
    
    simulator_data_loader = Simulation_data_loader(game_data=game_classes)
    
    simulator = Brute_force_simulation_bonus_check(
        equipment_reader = simulator_data_loader.assemble_simul_equipment_from_game_data(),
        item_model_list = simulator_data_loader.assemble_item_model_list_from_game_data(),
        set_model_list = simulator_data_loader.assemble_item_set_model_list_from_game_data()
    )
    
    weapon_rule = WeaponDamageSimulRule()
    total_skill_rule = TotalSkillPointsRule()
    
    rule_set = SimulFitnessRuleSet(
                                    [weapon_rule,
                                    total_skill_rule
                                    ])
    
    equipment_result = simulator.maximum_equipment_greedy(simul_rule_set = rule_set)
    
    equipment_result.equip()