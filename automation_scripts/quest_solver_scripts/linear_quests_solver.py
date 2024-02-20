import typing

from the_west_inner.game_classes import Game_classes
from the_west_inner.requests_handler import requests_handler
from the_west_inner.linear_quest_manager import LinearQuestManager,LinearQuest
from the_west_inner.quest_requirements import Quest_requirement_duel_quest_npc

from automation_scripts.quest_solver_scripts.quest_solver_builder import QuestSolverBuilder

class LinearQuestSolver :
    
    def __init__(self ,
                 game_classes : Game_classes,
                 linear_quest_manager: LinearQuestManager
                 ):
        self.game_classes = game_classes
        self.linear_quest_manager = linear_quest_manager
        self.solver_builder = QuestSolverBuilder(game_classes=self.game_classes,
                                                 energy_consumable_id= None
                                                 )
        self.current_quest = linear_quest_manager.current_quest
        
    def solve(self):
        
        while not self.linear_quest_manager.is_completed:
            
            quest_to_solve = self.linear_quest_manager.current_quest
            print(f'Solving quest {quest_to_solve.quest_id}')
            
            if not quest_to_solve.accepted:
                self.linear_quest_manager.accept_quest()
            if quest_to_solve.finishable:
                self.linear_quest_manager.complete_quest()
                continue
            requirements = quest_to_solve.requirements
            requirements.sort(key=lambda x : x.priority)
            
            for requirement in requirements:
                solver = self.solver_builder.build(quest_requirement = requirement)
                if solver is None:
                    continue
                solve_result = solver.solve()
                
                if not solve_result:
                    return False
            
            quest_to_solve = quest_to_solve.update_quest(handler=self.game_classes.handler)
            if (quest_to_solve.finishable or
                len(requirements) == 0 or 
                any((isinstance(x,Quest_requirement_duel_quest_npc) for x in quest_to_solve.requirements))
                ):
                
                self.linear_quest_manager.complete_quest()
        