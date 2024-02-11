import typing

from gold_finder import parse_map_for_quest_employers
from work_manager import Work_manager
from requests_handler import requests_handler
from crafting import Crafting_table,acquire_product
from items import Items
from game_classes import Game_classes
from marketplace_buy import Marketplace_categories,search_marketplace_category,search_marketplace_item
from marketplace import Marketplace_buy_manager

class Quest_requirement():
    def __init__(self,solved):
        self.solved = solved
    def declare_solved(self):
        self.solved = True
class Quest_requirement_travel(Quest_requirement):
    priority = 3
    def __init__(self,x:int,y:int,employer_key:str,quest_id:int,solved:bool):
        self.x = x
        self.y = y
        self.employer_key = employer_key
        self.quest_id = quest_id
        self.solved = solved
    def declare_solved(self):
        return super().declare_solved()
class Quest_requirement_item_to_hand_work_product_hourly():
    priority = 1
    def __init__(self,item_id:int,number:int,quest_id:int,solved:bool):
        self.item_id = item_id
        self.number = number
        self.quest_id = quest_id
        self.solved = solved
    def declare_solved(self):
        return super().declare_solved()
class Quest_requirement_item_to_hand_work_product_seconds():
    priority = 1
    def __init__(self,item_id:int,number:int,quest_id:int,solved:bool):
        self.item_id = item_id
        self.number = number
        self.quest_id = quest_id
        self.solved = solved
    def declare_solved(self):
        return super().declare_solved()
class Quest_requirement_item_to_hand_buy_from_marketplace(Quest_requirement):
    priority = 1
    def __init__(self,item_id:int,number:int,quest_id:int,solved:bool):
        self.item_id = item_id
        self.number = number
        self.quest_id =quest_id
        self.solved = solved
    def declare_solved(self):
        return super().declare_solved()
class Quest_requirement_item_to_buy_from_city_building(Quest_requirement):
    priority = 1
    def __init__(self,item_id:int,number:int,quest_id:int,solved:bool):
        self.item_id = item_id
        self.number = number
        self.quest_id = quest_id
        self.solved = solved
    def declare_solved(self):
        return super().declare_solved()
class Quest_requirement_use_travelling_merchant_item(Quest_requirement):
    priority = 1
    
    def __init__(self,item_id:int , number:int , quest_id : int , solved:bool):
        
        self.item_id = item_id
        self.number = number
        self.quest_id = quest_id
        self.solved = solved
    def declare_solved(self):
        return super().declare_solved()
class Quest_requirement_item_to_get_from_other_quest(Quest_requirement):
    priority = 2
    def __init__(self,item_id:int,item_id_reward_quest:int,quest_id:int,solved:bool):
        self.item_id = item_id
        self.item_id_reward_quest = item_id_reward_quest
        self.quest_id = quest_id
        self.solved = solved
    def declare_solved(self):
        return super().declare_solved()

class Quest_requirement_work_n_seconds(Quest_requirement):
    priority = 1
    def __init__(self,work_id : int , required_work_time : int,solved:bool):
        self.work_id = work_id
        self.required_work_time = required_work_time
        self.solved = solved
    
    def declare_solved(self):
        return super().declare_solved()

class Quest_requirement_work_n_times(Quest_requirement):
    priority = 1
    def __init__(self,work_id : int , required_work_times : int,solved:bool):
        self.work_id = work_id
        self.required_work_times = required_work_times
        self.solved = solved
    
    def declare_solved(self):
        return super().declare_solved()

class Quest_requirement_sell_item(Quest_requirement):
    priority = 2
    def __init__(self, item_id: int , solved : bool ):
        self.item_id = item_id
        self.solved = solved
    
    def declare_solved(self):
        return super().declare_solved()

class Quest_requirement_accept_other_quest(Quest_requirement):
    priority = 1
    def __init__(self , other_quest_id : int , solved : bool ):
        self.other_quest_id = other_quest_id
        self.solved = solved
    
    def declare_solved(self):
        return super().declare_solved()
 
class Quest_requirement_solve_other_quest(Quest_requirement):
    priority = 1
    def __init__(self , other_quest_id : int , solved : bool ):
        self.other_quest_id = other_quest_id
        self.solved = solved
    
    def declare_solved(self):
        return super().declare_solved()

class Quest_requirement_distribute_skill_point(Quest_requirement):
    priority = 1
    def __init__(self, solved):
        self.solved = solved
    def declare_solved(self):
        return super().declare_solved()


class Quest_requirement_duel_npc(Quest_requirement):
    priority = 1
    def __init__(self,quest_id:int,solved:bool):
        self.quest_id = quest_id
        self.solved = solved
    def declare_solved(self):
        return super().declare_solved()
class Quest_requirement_duel_quest_npc(Quest_requirement):
    priority = 3
    def __init__(self,quest_id:int,solved = True):
        self.quest_id = quest_id
        self.solved = solved



#class UnknownQuestRequirement(Exception):
#    pass
#def sort_quest_requirement(requirement_dict:dict,handler:requests_handler):
#    match requirement_dict:
#        case []:
#            Quest_requirement()
#        case _ if 'jsInfo' in requirement_dict and requirement_dict['jsInfo']['type'] == "task-finish-walk":
#            return Quest_requirement_travel_builder(requirement_dict=requirement_dict,handler=handler).build()
#        case _ if 'jsInfo' in requirement_dict and requirement_dict['jsInfo']['type'] == "inventory_changed":
#            return "TO DO!"
#        case _ :
#            raise UnknownQuestRequirement()

    

class Quest_requirement_list():
    def __init__(self,requirement_list:list[Quest_requirement]):
        self.requirement_list = requirement_list
    
    @property
    def solved_requirements(self):
        return all([x.solved for x in self.requirement_list])

def build_solved_quest_requirement(requirement_dict_iterables:typing.Iterable):
    requirements = []
    for requirement_dict in requirement_dict_iterables:
        requirements.append(Quest_requirement(solved=requirement_dict['solved']))
    return Quest_requirement_list(requirement_list = requirements)