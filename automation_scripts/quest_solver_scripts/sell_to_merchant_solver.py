from the_west_inner.bag import Bag
from the_west_inner.items import Items
from the_west_inner.currency import Currency

from the_west_inner.quest_requirements import Quest_requirement_sell_item
from the_west_inner.requests_handler import requests_handler

from the_west_inner.traveling_merchant import Travelling_merchant_manager

from automation_scripts.mass_item_sell.sell import SellDecisionManager , SellManager


class SellToMerchantQuestSolver():
    
    def __init__(self,
                 quest_requirement : Quest_requirement_sell_item,
                 handler : requests_handler,
                 bag : Bag,
                 items : Items,
                 currency : Currency
                 ) :
        self.quest_requirement = quest_requirement
        self.handler = handler
        self.bag = bag
        self.items = items
        self.currency = currency
    
    def solve(self) -> bool:
        
        
        
        merchant = Travelling_merchant_manager(
        handler = self.handler,
        bag = self.bag,
        items= self.items,
        currency = self.currency
        )
        if self.quest_requirement.item_id not in self.bag:
            return False
        merchant.sell_item(
            item_id = self.quest_requirement.item_id
        )
        self.quest_requirement.declare_solved()
        return True