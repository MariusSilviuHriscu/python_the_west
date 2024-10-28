from the_west_inner.game_classes import Game_classes
from the_west_inner.quest_requirements import Quest_requirement_solve_other_quest

from automation_scripts.quest_solver_scripts.quest_solver_manager import build_quest_group_solver_manager

class SolveOtherQuestSolver:
    
    def __init__(self,
                quest_requirement : Quest_requirement_solve_other_quest ,
                game_classes : Game_classes
                ):
        
        self.quest_requirement  = quest_requirement
        self.game_classes = game_classes
    
    def solve(self) -> bool:
        
        solver = build_quest_group_solver_manager(
            game_classes = self.game_classes,
            target_quest_group_data = self.quest_requirement.other_quest_data
        )
        
        return solver.solve()
    