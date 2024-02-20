from the_west_inner.requests_handler import requests_handler
from the_west_inner.work_manager import Work_manager
from the_west_inner.player_data import Player_data
from the_west_inner.bag import Bag
from the_west_inner.work import Work,Work_list,get_closest_workplace_data
from the_west_inner.game_classes import Game_classes

from automation_scripts.work_cycle import Script_work_task

from the_west_inner.quest_requirements import Quest_requirement_work_quest_item

class WorkForQuestItemQuestSolver :

    def __init__(self,
                 quest_requirement : Quest_requirement_work_quest_item,
                 handler : requests_handler,
                 player_data : Player_data,
                 bag : Bag,
                 work_manager : Work_manager,
                 game_classes : Game_classes
                 ):
        
        self.quest_requirement = quest_requirement
        self.handler = handler
        self.player_data = player_data
        self.bag = bag
        self.work_manager = work_manager
        self.game_classes = game_classes
    def solve(self):
        
        maximum_actions = self.player_data.energy
        if maximum_actions == 0 :
            return False
        job_id,job_x,job_y = get_closest_workplace_data(
            handler = self.handler,
            job_id = self.quest_requirement.work_id,
            job_list = self.work_list,
            player_data = self.player_data
        )
        
        self.bag.update_inventory(handler=self.handler)
        
        if self.bag[self.quest_requirement.item_id] <= 1:
            self.quest_requirement.declare_solved()
            return True
        
        while self.bag[self.quest_requirement.item_id] == 0:
            work_data = Work(job_id=job_id,x=job_x,y= job_y,duration=15)
            work_task = Script_work_task(
                work_manager = self.work_manager,
                work_data=work_data,
                number_of_actions = 1,
                game_classes = self.game_classes
            )
            
            work_task.execute()
            self.bag.update_inventory(handler=self.handler)
            
            maximum_actions -= 1
            if maximum_actions ==0:
                return False
        self.quest_requirement.declare_solved()
        return True