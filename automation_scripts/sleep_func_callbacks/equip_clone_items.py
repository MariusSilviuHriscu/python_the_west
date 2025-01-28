

from the_west_inner.game_classes import Game_classes
from the_west_inner.simulation_data_library.genetic_item_selection import run_genetic_algorithm_simulation
from the_west_inner.simulation_data_library.simul_equip_fitnes import SimulFitnessRuleSet
from the_west_inner.simulation_data_library.simul_equip_rules.luck_rule import ProductDropSimulRule
from the_west_inner.simulation_data_library.simul_equip_rules.total_skill_points_rule import TotalSkillPointsRule


def clone_equip(game_classes : Game_classes):
    if None not in game_classes.equipment_manager.current_equipment:
        return
    
    product_drop_rule = ProductDropSimulRule()
    total_workpoints = TotalSkillPointsRule()

    
    rule_set = SimulFitnessRuleSet([product_drop_rule,total_workpoints])
    
    new_equipment = run_genetic_algorithm_simulation(
        game_data= game_classes,
        fitness_rule_set = rule_set
    )
    
    
    print(new_equipment)
    new_equipment.equip(handler = game_classes.handler,
                        equipment_manager = game_classes.equipment_manager
                        )
    