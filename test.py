from the_west_inner.movement_manager import MovementManager
from the_west_inner.login import Game_login
from the_west_inner.map import Map
from the_west_inner.marketplace_sell import Auction_sell_manager
from the_west_inner.marketplace_pickup_manager import MarketplacePickupManager
from the_west_inner.marketplace import build_marketplace_managers
from automation_scripts.marketplace_scripts.marketplace_observer import build_market_observer,MarketBuyTarget
from automation_scripts.product_work_cycle import CycleJobsProducts
from the_west_inner.work import Work
from automation_scripts.work_cycle import Cycle_jobs
from automation_scripts.sleep_func_callbacks.callback_chain import CallbackChainer
from automation_scripts.sleep_func_callbacks.misc_func_callback import read_report_rewards,recharge_health,check_and_update_skills
from automation_scripts.sleep_func_callbacks.callback_frequency import RandomRunRule,CallableRunRule
from the_west_inner.traveling_merchant import (
                                        Travelling_market_offer,
                                        Travelling_merchant_manager,
                                        TravellingMerchantOfferSearchManager,
                                        Travelling_merchant_type_enum
                                        )

from the_west_inner.skills import read_skill

from automation_scripts.sleep_func_callbacks.misc_func_callback import check_and_update_skills

from the_west_inner.duels import NpcDuelManager


from the_west_inner.linear_quest_manager import LinearQuestManager

from automation_scripts.quest_solver_scripts.linear_quests_solver import LinearQuestSolver
from automation_scripts.quest_solver_scripts.quest_solver_builder import QuestSolverBuilder
from the_west_inner.saloon import SolvedQuestManager
from the_west_inner.saloon import load_all_available_quest_employers_data_list


login = Game_login(player_name='hmrsu',player_password='numaiteconecta69',world_id=1)#7)
game_classes = login.login()

from automation_scripts.quest_solver_scripts.quest_requirement_data.quest_group_data import assemble_quest_group_linked_list,QuestGroupData
from automation_scripts.quest_solver_scripts.quest_solver_manager import QuestGroupSolverManager,build_quest_group_solver_manager

from automation_scripts.quest_solver_scripts.quest_requirement_data.quest_group_1 import GROUP_1
from automation_scripts.quest_solver_scripts.quest_requirement_data.quest_group_4 import GROUP_4
from automation_scripts.quest_solver_scripts.quest_requirement_data.quest_group_5 import GROUP_5
from automation_scripts.quest_solver_scripts.quest_requirement_data.quest_group_17 import GROUP_17
from automation_scripts.quest_solver_scripts.quest_requirement_data.quest_group_55 import GROUP_55

grup = [GROUP_1,GROUP_4,GROUP_5,GROUP_17,GROUP_55]

a = assemble_quest_group_linked_list(grup,4)

chainer = CallbackChainer()
chainer.add_callback(check_and_update_skills,
                     handler = game_classes.handler,
                     target_attribute_key = "strength" ,
                     target_skill_key = "build")

from the_west_inner.simulation_data_library.simul_equipment import _game_data_to_current_equipment
from the_west_inner.simulation_data_library.calc_maxim import Brute_force_simulation_bonus_check
from the_west_inner.simulation_data_library.simul_items import Item_list,create_item_list_from_model,Item_model_list,Weapon_damage_range
from the_west_inner.simulation_data_library.load_items_script import get_simul_items,get_simul_sets
from the_west_inner.simulation_data_library.simul_sets import create_set_instance_list,Item_set_list
from the_west_inner.item_set_general import get_item_sets,Item_sets
from the_west_inner.simulation_data_library.simul_equipment import create_simul_equipment_by_current_equipment
from the_west_inner.simulation_data_library.simul_equip_fitnes import SimulFitnessRuleSet
from the_west_inner.simulation_data_library.simul_equip_rules.weapon_damage_rule import WeaponDamageSimulRule


raw_sets = get_item_sets(requests_handler= game_classes.handler)
sets = get_simul_sets(
                    sets= raw_sets
                    )
set_list = Item_set_list(sets)
list_of_item_models = get_simul_items(
                                    bag = game_classes.bag,
                                    current_equipment = game_classes.equipment_manager.current_equipment,
                                    items = game_classes.items
                                    )
item_model_list = Item_model_list(item_model_list = list_of_item_models)
print(item_model_list.calc_permutations())
item_model_list = item_model_list.filter_mapdrop_items()
print(item_model_list.calc_permutations())
item_model_list = item_model_list.filter_by_player_level(player_level=game_classes.player_data.level)
print(item_model_list.calc_permutations())
item_model_list = item_model_list.filter_out_usables()
print(item_model_list.calc_permutations())
#item_model_list = item_model_list.filter_setless_items()
#print(item_model_list.calc_permutations())

equip_simul = _game_data_to_current_equipment(game_data=game_classes)

sim = Brute_force_simulation_bonus_check(
    equipment_reader = equip_simul,
    item_model_list=item_model_list,
    set_model_list=set_list
)

weapon_rule = WeaponDamageSimulRule()
rule_set = SimulFitnessRuleSet(
    [weapon_rule]
)

a = sim.maximum_equipment_value_brute_force(simul_rule_set=rule_set)
b = sim.maximum_equipment_greedy(simul_rule_set=rule_set)