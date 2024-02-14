from the_west_inner.quest_requirements import Quest_requirement_distribute_skill_point
from the_west_inner.requests_handler import requests_handler

from the_west_inner.skills import read_skill

class DistributeSkillPointsQuestSolver():
    
    def __init__(self,
                 quest_requirement:Quest_requirement_distribute_skill_point,
                 handler:requests_handler,
                 skill_target_key : str
                 ):
        
        self.quest_requirement = quest_requirement
        self.handler = handler
        self.skill_target_key = skill_target_key
    
    def solve(self) :
        
        skills = read_skill(handler = self.handler)
        
        if self.quest_requirement.number_of_skill_points > skills.open_skill_points :
            return False
        
        skills.save_additional_skills_attributes({self.skill_target_key : self.quest_requirement.number_of_skill_points})
        
        
        return True