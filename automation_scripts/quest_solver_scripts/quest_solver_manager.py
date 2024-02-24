from the_west_inner.game_classes import Game_classes
from the_west_inner.quest_requirements import Quest_requirement,Quest_requirement_travel
from the_west_inner.saloon import Quest,QuestEmployerDataList,Quest_employer,SolvedQuestManager
from the_west_inner.saloon import (QuestNotCompletedError,
                                   QuestNotAcceptable,
                                   QuestNotAccepted,
                                   QuestNotFinishable
                                   )


from quest_solver_builder import QuestSolverBuilder


from automation_scripts.quest_solver_scripts.quest_requirement_data.quest_group_data import QuestGroupData


class QuestSolver :
    
    def __init__(self, 
                game_classes : Game_classes,
                quest : Quest,
                employer: Quest_employer,
                requirement_solution_builder : QuestSolverBuilder ,
                quest_complete_requirements : list[Quest_requirement]
                ):
        
        self.game_classes = game_classes
        self.employer = employer
        self.requirement_solution_builder = requirement_solution_builder
        self.quest_complete_requirements = quest_complete_requirements
        self.quest = quest
    
    def _complete_requirements(self,quest_requirements : list[Quest_requirement]):
        
        quest_requirements.sort(lambda x: x.priority)

        for requirement in quest_requirements:
            
            solver = self.requirement_solution_builder.build(quest_requirement = requirement)
            solution_status = solver.solve()
            if not solution_status :
                return False
        return True
    def reload_quest(self):
        self.employer.reload_data(handler = self.game_classes.handler)
    def go_to_employer(self):
        requirement = Quest_requirement_travel(x = self.quest.employer_coords[0],
                                               y = self.quest.employer_coords[1],
                                               employer_key = self.quest.employer_key,
                                               quest_id = self.quest.quest_id,
                                               solved = False
                                               )
        self.requirement_solution_builder.build(quest_requirement=requirement).solve()
        self.reload_quest()
    def accept_quest_solver(self) -> bool:
        if self.quest.is_accepted:
            return True
        if self.quest.employer_coords :
            self.go_to_employer()
        
        if not self.quest.is_acceptable :
            raise QuestNotAcceptable('Something went wrong when trying to accept quest!')
        
        self.quest.accept_quest(handler=self.game_classes.handler)
        self.reload_quest()
        if not self.quest.is_accepted:
            raise QuestNotAccepted(f'The quest {self.quest.quest_id} : {self.quest.group_title} couldn t be accepted !')
    def solve_quest(self) -> bool:
        
        result_status = self._complete_requirements(quest_requirements = self.quest_complete_requirements)
        if not result_status:
            return result_status
        
        if not self.quest.is_completed:
            raise QuestNotCompletedError(f"You were about to try to finish a quest you didn't complete ")
        
        if self.quest.employer_coords :
            self.go_to_employer()
        
        self.reload_quest()
        
        if not self.quest.is_finishable:
            raise QuestNotFinishable('You cannot complete a quest that is not finishable ! ')
        
        self.quest.complete_quest(handler = self.game_classes.handler)
        
        return True
        
class QuestGroupSolverManager:
    
    def __init__(self , 
                 game_classes : Game_classes,
                 requirement_solution_builder : QuestSolverBuilder ,
                 available_employer_data : QuestEmployerDataList,
                 solved_quest_manager : SolvedQuestManager , 
                 quest_group_data : QuestGroupData
                 ):
        self.game_classes = game_classes
        self.requirement_solution_builder = requirement_solution_builder
        self.quest_group_data = quest_group_data
        self.available_employer_data = available_employer_data
        self.solved_quest_manager = solved_quest_manager
    
    def quest_is_solved(self,quest_id:int) -> bool:
        
        return self.solved_quest_manager.has_completed_quest(quest_id=quest_id)
    @property
    def quest_group_is_completed(self) -> bool:
    
        last_quest_id = self.quest_group_data.last_quest_id
        
        return self.quest_is_solved(quest_id=last_quest_id)
    
    def _solve(self,quest_group_data :QuestGroupData) ->bool:
        
        for quest_id,quest_requirements in self.quest_group_data.iter_requirements(reverse=True):
            
            if self.solved_quest_manager.has_completed_quest(quest_id = quest_id) :
                
                return True