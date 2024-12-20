import time
import typing

from the_west_inner.game_classes import Game_classes
from the_west_inner.equipment import Equipment,Equipment_manager
from the_west_inner.quest_requirements import Quest_requirement,Quest_requirement_travel
from the_west_inner.saloon import Quest,QuestEmployerDataList,Quest_employer,SolvedQuestManager,load_all_available_quest_employers_data_list
from the_west_inner.saloon import (QuestNotCompletedError,
                                   QuestNotAcceptable,
                                   QuestNotAccepted,
                                   QuestNotFinishable,
                                   DuelQuestFinishError
                                   )
from the_west_inner.quest_requirements import Quest_requirement_duel_quest_npc

from automation_scripts.sleep_func_callbacks.callback_chain import CallbackChainer

from automation_scripts.quest_solver_scripts.quest_solver_builder import QuestSolverBuilder


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
        
        quest_requirements.sort(key = lambda x: x.priority)

        for requirement in quest_requirements:
            if isinstance(requirement,Quest_requirement_duel_quest_npc):
                continue
            solver = self.requirement_solution_builder.build(quest_requirement = requirement)
            if solver is None:
                return False
            solution_status = solver.solve()
            time.sleep(1)
            if not solution_status :
                return False
        return True
    def reload_quest(self):
        
        # The server takes a while to process the quest state so if I didn't sleep here the returned data would be the same as before , making the whole call useless
        time.sleep(1)
        self.employer = self.employer.reload_data(handler = self.game_classes.handler)
        self.quest = self.employer.get_quest_by_id(quest_id=self.quest.quest_id)
    def go_to_employer(self):
        
        requirement = Quest_requirement_travel(x = self.quest.employer_coords[0][0],
                                               y = self.quest.employer_coords[0][1],
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
        return True
    def solve_quest(self) -> bool:
        if not self.quest.is_solved:
            
            result_status = self._complete_requirements(quest_requirements = self.quest_complete_requirements)
            if not result_status:
                return result_status
            self.reload_quest()
            if (not self.quest.is_solved and not 
                any((isinstance(x,Quest_requirement_duel_quest_npc) for x in self.quest_complete_requirements)) 
                and not len(self.quest_complete_requirements) == 0
                and not self.quest.employer_coords):
                print(self.quest.__dict__)
                raise QuestNotCompletedError(f"You were about to try to finish a quest you didn't complete ")
        
        if self.quest.employer_coords :
            self.go_to_employer()
            self.reload_quest()
        
        if (not self.quest.is_finishable and not 
            any((isinstance(x,Quest_requirement_duel_quest_npc) for x in self.quest_complete_requirements)) ):
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

        self._duel_equipment = None
        self._callback_chainer : CallbackChainer = None
    def set_failed_duel_callback(self,callback_chainer:CallbackChainer):
        
        self.callback_chainer = callback_chainer
    @property
    def duel_equipment(self) -> Equipment|None:
        return self._duel_equipment
    def callback_function(self) -> typing.Callable:
        return self.callback_chainer.chain_function()
    def set_duel_equipment(self,equipment : Equipment) :
        
        self._duel_equipment = equipment
        
    def quest_is_solved(self,quest_id:int) -> bool:
        
        return self.solved_quest_manager.has_completed_quest(quest_id=quest_id)
    @property
    def quest_group_is_completed(self) -> bool:
    
        last_quest_id = self.quest_group_data.last_quest_id
        
        return self.quest_is_solved(quest_id=last_quest_id)
    
    def solve(self) ->bool:
        
        for quest_info in self.quest_group_data.list_quest_info():
            
            
            if self.solved_quest_manager.has_completed_quest(quest_id = quest_info.quest_id) :
                print(f"We already solved quest {quest_info.quest_id} from the group {quest_info.quest_group}")
                continue
            
            print(f"We are solving quest {quest_info.quest_id} from the group {quest_info.quest_group}")
            quest_employer_data = load_all_available_quest_employers_data_list(handler = self.game_classes.handler)
            quest_employer = quest_employer_data.get_employer_by_quest_id(quest_id = quest_info.quest_id)
            quest = quest_employer.get_quest_by_id(quest_id=quest_info.quest_id)
            
            solver = QuestSolver(game_classes=self.game_classes,
                                 quest = quest,
                                 employer= self.available_employer_data.get_employer_by_quest_id(quest_id = quest_info.quest_id),
                                 requirement_solution_builder = self.requirement_solution_builder,
                                 quest_complete_requirements= quest_info.quest_requirements
                                 )
            if not solver.accept_quest_solver():
                return False
            if quest.is_duel and self.duel_equipment is not None:
                current_equipment = self.game_classes.equipment_manager.current_equipment
                self.game_classes.equipment_manager.equip_equipment(equipment=self._duel_equipment,
                                                                    handler=self.game_classes.handler
                                                                    )
            try:
                if not solver.solve_quest():
                    return False
            except DuelQuestFinishError as e:
                if self._callback_chainer is not None:
                    self.callback_function()
                if not solver.solve_quest():
                    return False
            except Exception as e:
                raise e
            finally :
                if quest.is_duel and self.duel_equipment is not None:
                    self.game_classes.equipment_manager.equip_equipment(equipment=current_equipment,
                                                                        handler=self.game_classes.handler
                                                                        )
                
            self.solved_quest_manager.update_data()
        return True

def build_quest_group_solver_manager(game_classes : Game_classes ,
                                    target_quest_group_data : QuestGroupData,
                                    chainer :CallbackChainer = None
                                    ):
    solver_manager = QuestGroupSolverManager(
        game_classes = game_classes,
        requirement_solution_builder = QuestSolverBuilder(
                                                        game_classes = game_classes,
                                                        energy_consumable_id = None
                                                        ),
        available_employer_data = load_all_available_quest_employers_data_list(handler=game_classes.handler),
        solved_quest_manager = SolvedQuestManager(
            handler = game_classes.handler),
        quest_group_data = target_quest_group_data

    )
    if chainer is not None:
        solver_manager.set_failed_duel_callback(callback_chainer=chainer)
    
    return solver_manager