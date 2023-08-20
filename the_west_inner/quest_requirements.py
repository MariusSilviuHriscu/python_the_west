import typing

from gold_finder import parse_map_for_quest_employers
from work_manager import Work_manager
from requests_handler import requests_handler
from crafting import Crafting_table,fa_rost
from items import Items
from game_classes import Game_classes
from marketplace_buy import Marketplace_categories,search_marketplace_category,search_marketplace_item
from marketplace import Marketplace_buy_manager

class Quest_requirement():
    def __init__(self,solved):
        self.solved = solved
    def solve():
        pass
    def declare_solved(self):
        self.solved = True

class Quest_Reward():
    pass


class Quest_requirement_travel(Quest_requirement):
    priority = 3
    def __init__(self,x:int,y:int,employer_key:str,quest_id:int,solved:bool):
        self.x = x
        self.y = y
        self.employer_key = employer_key
        self.quest_id = quest_id
        self.solved = solved
    def solve(self,work_manager:Work_manager):
        
        work_manager.move_to_quest_employer(quest_employer_key=self.employer_key,x=self.x,y=self.y)
        
        work_manager.wait_until_free_queue()
        
        return True
    def declare_solved(self):
        self.solved = True

class QuestEmployerNotFound(Exception):
    pass

class Quest_requirement_travel_builder():
    def __init__(self,requirement_dict:dict,handler:requests_handler):
        self.requirement_dict = requirement_dict
        self.handler = handler
        self.quest_id = self.requirement_dict['id']
    def _get_employer_data(self,employer_info:str) ->dict[str,int|str]:
        map_employers = parse_map_for_quest_employers(handler = self.handler )
        for location in map_employers:
            for employer in location['employer']:
                if employer['name'] in employer_info:
                    return {
                            'employer_key' : employer['key'],
                            'x' : location['x'],
                            'y' : location['y']
                            }
        raise QuestEmployerNotFound(f"Could not find the correct employer : {employer_info}")
    def build(self):
        employer_data = self._get_employer_data(employer_info=self.requirement_dict['info'])
        return Quest_requirement_travel(
                                        x = employer_data.get("x"),
                                        y = employer_data.get("y"),
                                        employer_key= employer_data.get("employer_key")
                                        )
class Quest_requirement_item_to_hand_work_product():
    priority = 1
    def __init__(self,item_id:int,number:int,quest_id:int,solved:bool):
        self.item_id = item_id
        self.number = number
        self.quest_id = quest_id
        self.solved = solved
    def solve(self,game_classes:Game_classes):
        fa_rost(id_item=self.item_id,nr=self.number,game_classes=game_classes)
        while game_classes.bag[self.item_id] < self.number:
            game_classes.work_manager.wait_until_free_queue()
            fa_rost(id_item=self.item_id,nr=self.number,game_classes=game_classes)
        return True
    def declare_solved(self):
        self.solved = True

class QuestMarketplaceItemSearchError(Exception):
    pass
class Quest_requirement_item_to_hand_buy_from_marketplace(Quest_requirement):
    priority = 1
    def __init__(self,item_id:int,number:int,quest_id:int,solved:bool):
        self.item_id = item_id
        self.number = number
        self.quest_id =quest_id
        self.solved = solved
    def solve(self,game_classes : Game_classes):
        while game_classes.bag[self.item_id] <= self.number:
            marketplace_buy_manager = Marketplace_buy_manager(handler = game_classes.handler)
            marketplace_buy_manager.buy_cheapest_and_pick_up(item_id = self.item_id)
    def declare_solved(self):
        self.solved = True
class Quest_requirement_item_to_buy_from_city_building(Quest_requirement):
    priority = 1
    def __init__(self,item_id:int,number:int,quest_id:int,solved:bool):
        self.item_id = item_id
        self.number = number
        self.quest_id = quest_id
        self.solved = solved
    def solve(self,game_classes:Game_classes):
        raise NotImplementedError("Town stuff is not implemented yet...")
    def declare_solved(self):
        return super().declare_solved()
class Quest_requirement_item_to_get_from_other_quest(Quest_requirement):
    priority = 2
    def __init__(self,item_id:int,item_id_reward_quest:int,quest_id:int,solved:bool):
        self.item_id = item_id
        self.item_id_reward_quest = item_id_reward_quest
        self.quest_id = quest_id
        self.solved = solved
    def solve(self):
        raise NotImplementedError("Not implemented the solve other quest....")
    def declare_solved(self):
        return super().declare_solved()
class Quest_requirement_item_to_hand_builder():
    def __init__(self,requirement_dict:dict,handler:requests_handler):
        self.requirement_dict = requirement_dict
        self.handler = handler
    def _get_item_id(self):
        """
        Private function to help you get the quest requirement target id.
        """
        return self.requirement_dict['jsInfo']['id']
    def _figure_item_type(self,game_classes:Game_classes):
        nominal_item_type = game_classes.items.get_item(item_id = self._get_item_id() )['type']
        if nominal_item_type == 'yield':
            if self._get_item_id() in game_classes.crafting_table and game_classes.crafting_table[self._get_item_id()].profession != game_classes.player_data.profession:
                pass
            else:
                pass

class Quest_requirement_duel_npc(Quest_requirement):
    priority = 1
    def __init__(self,quest_id:int,solved:bool):
        self.quest_id = quest_id
        self.solved = solved
    
    def solve(self,game_classes:Game_classes):
        raise NotImplementedError("The duel npc managers are not yet implemented!")
    def declare_solved(self):
        return super().declare_solved()

class Quest_requirement_duel_quest_npc(Quest_requirement):
    priority = 3
    def __init__(self,quest_id:int,solved = True):
        self.quest_id = quest_id
        self.solved = solved
    def solve():
        pass

class Quest_duel_builder():
    def __init__(self,requirement_dict:dict,quest_id:int,handler:requests_handler):
        self.requirement_dict = requirement_dict
        self.handler = handler
        self.quest_id = quest_id
    def build(self):
        return Quest_requirement_duel_quest_npc(
                                                quest_id = self.quest_id,
                                                )


class UnknownQuestRequirement(Exception):
    pass
def sort_quest_requirement(requirement_dict:dict,handler:requests_handler):
    match requirement_dict:
        case []:
            Quest_requirement()
        case _ if 'jsInfo' in requirement_dict and requirement_dict['jsInfo']['type'] == "task-finish-walk":
            return Quest_requirement_travel_builder(requirement_dict=requirement_dict,handler=handler).build()
        case _ if 'jsInfo' in requirement_dict and requirement_dict['jsInfo']['type'] == "inventory_changed":
            return "TO DO!"
        case _ :
            raise UnknownQuestRequirement()

    

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