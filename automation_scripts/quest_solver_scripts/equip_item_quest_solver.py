from the_west_inner.bag import Bag
from the_west_inner.equipment import Equipment_manager
from the_west_inner.items import Items
from the_west_inner.requests_handler import requests_handler


from the_west_inner.quest_requirements import Quest_requirement_equip_item


class EquipItemQuestSolver:
    def __init__(self,
                 handler : requests_handler,
                 quest_requirement:Quest_requirement_equip_item,
                 bag : Bag,
                 items : Items,
                 equipment_manager : Equipment_manager):
        self.handler = handler
        self.quest_requirement = quest_requirement
        self.bag = bag
        self.items = items
        self.equipment_manager = equipment_manager
    
    def solve(self):
        self.bag.update_inventory(handler=self.handler)
        if self.bag[self.quest_requirement.item_id] == 0:
            return False
        
        if self.quest_requirement.item_id in self.equipment_manager.current_equipment:
            self.quest_requirement.declare_solved()
            return True
        
        item_data_dict = self.items.find_item(item_id=self.quest_requirement.item_id)
        
        self.equipment_manager.equip_item(item_id = self.quest_requirement.item_id,
                                          handler = self.handler
                                          )
        
        self.quest_requirement.declare_solved()
        return True