from the_west_inner.requests_handler import requests_handler
from the_west_inner.game_classes import Game_classes
from the_west_inner.gold_finder import parse_map_for_quest_employers
from the_west_inner.items import Items
from the_west_inner.crafting import Crafting_table
from the_west_inner.player_data import Player_data

from the_west_inner.quest_requirements import (Quest_requirement_travel,
                                Quest_requirement_item_to_hand_work_product_hourly,
                                Quest_requirement_item_to_hand_work_product_seconds,
                                Quest_requirement_item_to_hand_buy_from_marketplace,
                                Quest_requirement_duel_quest_npc
                                )


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
class Quest_duel_builder():
    def __init__(self,requirement_dict:dict,quest_id:int,handler:requests_handler):
        self.requirement_dict = requirement_dict
        self.handler = handler
        self.quest_id = quest_id
    def build(self):
        return Quest_requirement_duel_quest_npc(
                                                quest_id = self.quest_id
                                                )
class Quest_requirement_item_to_hand_builder():
    def __init__(self,
                 requirement_dict:dict,
                 handler:requests_handler,
                 items:Items,
                 crafting_table : Crafting_table,
                 player_data : Player_data
                 ):
        self.requirement_dict = requirement_dict
        self.handler = handler
        self.items = items
        self.crafting_table = crafting_table
        self.player_data = player_data
    def _get_item_id(self) -> int:
        """
        Private function to help you get the quest requirement target id.
        """
        return self.requirement_dict['jsInfo']['id']
    def _get_required_item_number(self) -> int:
        return self.requirement_dict['jsInfo']['count']        
    def _is_craftable_by_different_proffesion(self , item_id : int) -> bool:
        
        return item_id in self.crafting_table and self.crafting_table[item_id].profession != self.player_data.profession
    
    def _is_craftable_by_own_proffesion(self , item_id : int) -> bool:

        return item_id in self.crafting_table and self.crafting_table[item_id].profession == self.player_data.profession
    
    
    
    def build(self,game_classes:Game_classes):
        item_id = self._get_item_id()
        nominal_item_type = game_classes.items.get_item(item_id = item_id )['type']
        
        if nominal_item_type == 'yield':
            if self._is_craftable_by_different_proffesion(item_id=item_id) :
                return Quest_requirement_item_to_hand_buy_from_marketplace(item_id=item_id,
                                                                           number = self._get_required_item_number()
                                                                           )
            elif self._is_craftable_by_own_proffesion(item_id = item_id):
                return Quest_requirement_item_to_hand_work_product_hourly(
                    item_id = item_id,
                    number = self._get_required_item_number(),
                    solved = False
                )
            else :
                raise NotImplementedError("Didn't manage to finish this method as i still have to " )