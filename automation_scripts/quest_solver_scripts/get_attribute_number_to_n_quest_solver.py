from the_west_inner.quest_requirements import Quest_requirement_get_n_attribute_points
from the_west_inner.requests_handler import requests_handler

from the_west_inner.skills import read_skill


class GetAttributeNumberToNQuestSolver():
    
    def __init__(self,
                 quest_requirement : Quest_requirement_get_n_attribute_points,
                 handler : requests_handler
                 ) :
        self.quest_requirement = quest_requirement
        self.handler = handler
    
    def solve(self):
        skills = read_skill(handler=self.handler)
        
        current_attribute_value = skills.get_attribute(attribute = self.quest_requirement.attribute_key)
        attribute_to_distribute = self.quest_requirement.target_number - current_attribute_value
                
        if attribute_to_distribute <= 0 :
            return True
        
        if skills.open_attr_points <= attribute_to_distribute:
            return False
        
        skills.save_additional_skills_attributes(
            handler= self.handler,
            changes = {self.quest_requirement.attribute_key : self.quest_requirement.target_number}
            )
        self.quest_requirement.declare_solved()
        return True
        