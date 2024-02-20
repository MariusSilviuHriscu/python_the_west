from the_west_inner.quest_requirements import Quest_requirement_work_n_times

from the_west_inner.requests_handler import requests_handler
from the_west_inner.work_manager import Work_manager
from the_west_inner.work import get_closest_workplace_data
from the_west_inner.work import Work_list,Work
from the_west_inner.game_classes import Game_classes
from the_west_inner.player_data import Player_data

from automation_scripts.work_cycle import Script_work_task

class WorkNTimesSolver:
    
    def __init__(self,
                 quest_requirement : Quest_requirement_work_n_times ,
                 handler : requests_handler ,
                 work_manager : Work_manager,
                 work_list : Work_list,
                 player_data : Player_data,
                 game_classes : Game_classes
                 ):
        
        self.quest_requirement = quest_requirement
        self.handler = handler
        self.work_manger = work_manager
        self.work_list = work_list
        self.player_data = player_data
        self.game_classes = game_classes
    
    def solve(self):
        
        if self.player_data.energy < self.quest_requirement.required_work_times:
            return False
        workplace = get_closest_workplace_data(handler=self.handler,
                                               job_id = self.quest_requirement.work_id,
                                               job_list = self.work_list,
                                               player_data = self.player_data
                                               )
        work_data = Work(job_id=self.quest_requirement.work_id,
                         x = workplace[1],
                         y= workplace[2],
                         duration=15
                         )
        tasks = Script_work_task(
                                work_manager=self.work_manger,
                                work_data = work_data,
                                number_of_actions = self.quest_requirement.required_work_times,
                                game_classes = self.game_classes
                                 )
        
        tasks.execute()
        
        self.quest_requirement.declare_solved()
        
        return True