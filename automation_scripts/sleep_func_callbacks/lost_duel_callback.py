from the_west_inner.game_classes import Game_classes

from the_west_inner.simulation_data_library.calc_maxim import Brute_force_simulation_bonus_check,Item_cycle_simulation
from the_west_inner.simulation_data_library.simul_equip_fitnes import SimulFitnessRuleSet
from the_west_inner.simulation_data_library.simul_equip_rules.weapon_damage_rule import WeaponDamageSimulRule
from the_west_inner.simulation_data_library.simul_equip_rules.total_skill_points_rule import TotalSkillPointsRule
from the_west_inner.simulation_data_library.calc_maxim import Simulation_data_loader

def low_level_npc_duel_loss_callback(
    game_classes : Game_classes
    ) -> None:
    
    simulator_data_loader = Simulation_data_loader(game_data=game_classes)
    
    simulator = Item_cycle_simulation(
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
    
    equipment_result = simulator.greedy_sort(simul_rule_set=rule_set,
                                             player_level=game_classes.player_data.level
                                             )
    
    equipment_result.equip(handler = game_classes.handler ,
                           equipment_manager = game_classes.equipment_manager
                           )