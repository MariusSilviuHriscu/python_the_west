from the_west_inner.quest_requirements import Quest_requirement_get_n_skill_points
from the_west_inner.requests_handler import requests_handler

from the_west_inner.skills import read_skill


class GetSkillNumberToNQuestSolver():
    
    def __init__(self,
                 quest_requirement : Quest_requirement_get_n_skill_points,
                 handler : requests_handler
                 ) :
        self.quest_requirement = quest_requirement
        self.handler = handler
    
    def solve(self):
        skills = read_skill(handler=self.handler)
        
        current_skill_value = skills.get_skill_value(skill=self.quest_requirement.skill_key)
        skills_to_distribute = self.quest_requirement.target_number - current_skill_value
        
        if skills_to_distribute <= 0 :
            return True
        
        if skills.open_skill_points <= skills_to_distribute:
            return False
        
        skills.save_additional_skills_attributes(
            {self.quest_requirement.skill_key : self.quest_requirement.target_number}
            )
        self.quest_requirement.declare_solved()
        return True
        