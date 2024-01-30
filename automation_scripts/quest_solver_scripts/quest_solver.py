from typing import Protocol

from the_west_inner.quest_requirements import (
                                                Quest_requirement_travel,
                                                Quest_requirement_item_to_hand_work_product,
                                                Quest_requirement_item_to_hand_buy_from_marketplace
                                                )

from the_west_inner.game_classes import Game_classes
from the_west_inner.bag import Bag
from the_west_inner.work_manager import Work_manager
from the_west_inner.marketplace_buy import Marketplace_buy_manager
from the_west_inner.marketplace_pickup_manager import MarketplacePickupManager
from the_west_inner.crafting import acquire_product

from automation_scripts.work_cycle import Script_work_task

class QuestSolver(Protocol):
    
    def __init__(self) -> None:
        pass
    def solve(self) -> bool:
        pass


class TravelQuestSolver():
    
    def __init__(self, travel_quest_requirement : Quest_requirement_travel,work_manager : Work_manager):
        
        self.travel_quest_requirement = travel_quest_requirement
        self.work_manager = work_manager
        
    def solve(self) -> bool:
        
        self.work_manager.move_to_quest_employer(
                                quest_employer_key = self.travel_quest_requirement.employer_key,
                                x = self.travel_quest_requirement.x ,
                                y = self.travel_quest_requirement.y
                                )
        self.work_manager.wait_until_free_queue()
    
        self.travel_quest_requirement.declare_solved()

        return True

class WorkItemQuestSolver():

    def __init__(self ,
                 quest_requierement : Quest_requirement_item_to_hand_work_product,
                 game_classes : Game_classes
                 ):
        self.quest_requirement = quest_requierement
        self.game_classes = game_classes
        
    def solve(self) -> bool:
        if self.game_classes.bag[self.quest_requirement.item_id] >= self.quest_requirement.number:
            self.quest_requirement.declare_solved()
            return True
        if self.game_classes.player_data.level < 20 :
            Script_work_task()
        acquire_product(
            id_item = self.quest_requirement.item_id ,
            nr = self.quest_requirement.number ,
            game_classes = self.game_classes       
        )
        return False

class MarketplaceItemQuestSolver():
    
    def __init__(self , 
                 quest_requirement : Quest_requirement_item_to_hand_buy_from_marketplace,
                 marketplace_buy_manager : Marketplace_buy_manager,
                 marketplace_pickup_manager : MarketplacePickupManager,
                 bag : Bag
                 ):
        self.quest_requirement = quest_requirement
        self.marketplace_buy_manager = marketplace_buy_manager
        self.marketplace_pickup_manager = marketplace_pickup_manager
        self.bag = bag
    def solve(self) -> bool:
        
        bought_item_dict = self.marketplace_pickup_manager.search_buy_offers().item_dict
        bought_item_number = bought_item_dict.get(self.quest_requirement.item_id,0)
        
        number_of_items_to_buy = self.quest_requirement.number - self.bag[self.quest_requirement.item_id] - bought_item_number
        number_of_items_to_buy = max(number_of_items_to_buy , 0)
        
        number_bought = self.marketplace_buy_manager.buy_cheapest_n_items(item_id = self.quest_requirement.item_id ,
                                                          item_number = number_of_items_to_buy ,
                                                          buy_anyway = True
                                                          )
        
        if number_bought == number_of_items_to_buy :
            
            self.marketplace_pickup_manager.fetch_all_bought()
            
            self.quest_requirement.declare_solved()

            return True
        return False
            
            