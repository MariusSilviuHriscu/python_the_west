from automation_scripts.quest_solver_scripts.linear_quests_solver import LinearQuestSolver
from automation_scripts.sleep_func_callbacks.map_callback_types import TypeMapping, TypeMappingList

from the_west_inner.bag import Bag
from the_west_inner.buffs import Buff_list
from the_west_inner.consumable import Consumable_handler, Cooldown
from the_west_inner.game_classes import Game_classes
from the_west_inner.items import Items
from the_west_inner.linear_quest_manager import LinearQuestManager
from the_west_inner.movement import Game_data
from the_west_inner.player_data import Player_data
from the_west_inner.premium import Premium
from the_west_inner.reports import Reports_manager
from the_west_inner.requests_handler import requests_handler
from the_west_inner.skills import Skills , read_skill
from the_west_inner.telegrams import Telegram_data_reader
from the_west_inner.traveling_merchant import Travelling_merchant_manager
from the_west_inner.work_list import Work_list
from the_west_inner.crafting import Crafting_table, Crafting
from the_west_inner.work_manager import Work_manager
from the_west_inner.equipment import Equipment_manager
from the_west_inner.currency import Currency
from the_west_inner.movement_manager import MovementManager
from the_west_inner.marketplace import Marketplace_managers, build_marketplace_managers
from the_west_inner.map import MapLoader

GAME_CLASSES_MAPPING = TypeMapping(
    origin_type = Game_classes,
    type_dict = {
        Game_classes : lambda x : x,
        Bag : lambda x : x.bag,
        Player_data : lambda x : x.player_data,
        Consumable_handler : lambda x : x.consumable_handler,
        requests_handler : lambda x : x.handler,
        Items : lambda x : x.items,
        Game_data : lambda x : x.game_data,
        Premium : lambda x : x.premium,
        Work_list : lambda x : x.work_list,
        Crafting_table : lambda x : x.crafting_table,
        Crafting : lambda x : x.player_crafting,
        Cooldown : lambda x: x.cooldown,
        Buff_list : lambda x: x.buff_list,
        Work_manager : lambda x: x.work_manager,
        Equipment_manager : lambda x : x.equipment_manager,
        Currency : lambda x : x.currency,
        MovementManager : lambda x: x.movement_manager,
        Marketplace_managers : lambda x : build_marketplace_managers(
                                            handler = x.handler,
                                            items= x.items,
                                            currency= x.currency,
                                            movement_manager= x.movement_manager,
                                            bag= x.bag,
                                            player_data= x.player_data),
        MapLoader : lambda x : MapLoader(
                                handler= x.handler,
                                player_data= x.player_data,
                                work_list= x.work_list
                            ),
        Reports_manager : lambda x : Reports_manager(
                                                    handler = x.handler
                                                    ),
        Skills : lambda x : read_skill(handler= x.handler ),
        Telegram_data_reader : lambda x : Telegram_data_reader(handler= x.handler),
        Travelling_merchant_manager : lambda x : Travelling_merchant_manager(
                                                                            handler = x.handler,
                                                                            bag= x.bag,
                                                                            items= x.items,
                                                                            currency= x.currency
                                                                            ),
        LinearQuestSolver : lambda x : LinearQuestSolver(
                                                        game_classes = x,
                                                        linear_quest_manager = LinearQuestManager(handler= x.handler)
                                                        )
    }
)

UNIVERSAL_MAPPING = TypeMappingList(
    type_map_list= [GAME_CLASSES_MAPPING]
)
