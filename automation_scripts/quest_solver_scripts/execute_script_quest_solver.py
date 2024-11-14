from the_west_inner.game_classes import Game_classes
from the_west_inner.quest_requirements import Quest_requirement_execute_script


class ExecuteScriptQuestSolver:
    def __init__(self,
                 game_classes : Game_classes ,
                 quest_requirement:Quest_requirement_execute_script
                 ):
        self.quest_requirement = quest_requirement
        self.game_classes = game_classes
    
    def solve(self):
        
        result = self.quest_requirement.script(self.game_classes)
        
        if result :
            self.quest_requirement.declare_solved()
        return result