from the_west_inner.game_classes import Game_classes

from automation_scripts.quest_solver_scripts.quest_solver import QuestSolver
from the_west_inner.quest_requirements import (Quest_requirement_duel_quest_npc,
                                               Quest_requirement_distribute_skill_point,
                                               Quest_requirement_item_to_hand_work_product_seconds,
                                               Quest_requirement_work_n_times,
                                               Quest_requirement_duel_npc,
                                               Quest_requirement_get_n_skill_points,
                                               Quest_requirement_get_n_attribute_points,
                                               Quest_requirement_equip_item,
                                               Quest_requirement_work_quest_item,
                                               Quest_requirement_sell_item,
                                               Quest_requirement_solve_other_quest,
                                               Quest_requirement
                                               )
from automation_scripts.quest_solver_scripts.work_n_times_quest_solver import WorkNTimesSolver
from automation_scripts.quest_solver_scripts.npc_duel_quest_solver import NpcDuelQuestSolver
from automation_scripts.quest_solver_scripts.get_skill_number_to_n_quest_solver import GetSkillNumberToNQuestSolver
from automation_scripts.quest_solver_scripts.get_attribute_number_to_n_quest_solver import GetAttributeNumberToNQuestSolver
from automation_scripts.quest_solver_scripts.second_item_quest_solver import WorkItemSecondsQuestSolver
from automation_scripts.quest_solver_scripts.equip_item_quest_solver import EquipItemQuestSolver
from automation_scripts.quest_solver_scripts.work_for_quest_item_quest_solver import WorkForQuestItemQuestSolver
from automation_scripts.quest_solver_scripts.sell_to_merchant_solver import SellToMerchantQuestSolver
from automation_scripts.quest_solver_scripts.other_quest_solver import SolveOtherQuestSolver

class QuestSolverBuilder:
    
    def __init__(self,
                 game_classes : Game_classes,
                 energy_consumable_id = None
                 ):
        self.game_classes = game_classes
        self.energy_consumable_id = energy_consumable_id
    def build_quest_requirement_work_n_times(self,quest_requirement:Quest_requirement) -> QuestSolver:
        return WorkNTimesSolver(
                    quest_requirement = quest_requirement,
                    handler = self.game_classes.handler,
                    work_manager = self.game_classes.work_manager,
                    work_list = self.game_classes.work_list,
                    player_data = self.game_classes.player_data,
                    game_classes = self.game_classes
                )
    def build_solve_other_quest(self , quest_requirement : Quest_requirement) -> QuestSolver:
        return SolveOtherQuestSolver(
            quest_requirement = quest_requirement,
            game_classes = self.game_classes
        )
    def build_sell_to_merchant_solver(self , quest_requirement : Quest_requirement) -> QuestSolver:
        return SellToMerchantQuestSolver(
            quest_requirement = quest_requirement,
            handler = self.game_classes.handler,
            bag = self.game_classes.bag,
            items = self.game_classes.items,
            currency = self.game_classes.currency
        )
    def build_npc_duel_quest_solver(self,quest_requirement:Quest_requirement) -> QuestSolver:
        return NpcDuelQuestSolver(
            quest_requirement=quest_requirement,
            handler= self.game_classes.handler,
            equipment_manager= self.game_classes.equipment_manager,
            player_data=self.game_classes.player_data,
            duel_equipment=None
        )
    def build_get_skill_number_to_n_quest_solver(self,quest_requirement:Quest_requirement) -> QuestSolver:
        return GetSkillNumberToNQuestSolver(
            quest_requirement = quest_requirement,
            handler = self.game_classes.handler
        )
    def build_get_attribute_number_to_n_quest_solver(self,quest_requirement:Quest_requirement) -> QuestSolver:
        return GetAttributeNumberToNQuestSolver(
            quest_requirement = quest_requirement,
            handler = self.game_classes.handler
        )
    def build_work_item_seconds_quest_solver(self,quest_requirement:Quest_requirement) -> QuestSolver:
        return WorkItemSecondsQuestSolver(
            quest_requirement=quest_requirement,
            game_classes=self.game_classes,
            energy_recharge_id = self.energy_consumable_id
        )
    def build_equip_item_quest_solver(self,quest_requirement:Quest_requirement) -> QuestSolver:
        return EquipItemQuestSolver(
            handler = self.game_classes.handler,
            quest_requirement = quest_requirement,
            bag = self.game_classes.bag,
            items = self.game_classes.items,
            equipment_manager = self.game_classes.equipment_manager
        )
    def build_work_for_quest_item_quest_solver(self,quest_requirement:Quest_requirement) -> QuestSolver:
        return WorkForQuestItemQuestSolver(
            quest_requirement = quest_requirement,
            handler = self.game_classes.handler,
            player_data = self.game_classes.player_data,
            bag=self.game_classes.bag,
            work_manager=self.game_classes.work_manager,
            game_classes=self.game_classes
        )
    def build(self,quest_requirement:Quest_requirement) -> QuestSolver:
        if isinstance(quest_requirement,Quest_requirement_duel_quest_npc):
            return None
        elif isinstance(quest_requirement,Quest_requirement_work_n_times):
            return self.build_quest_requirement_work_n_times(quest_requirement = quest_requirement)
        elif isinstance(quest_requirement,Quest_requirement_duel_npc):
            return self.build_npc_duel_quest_solver(quest_requirement=quest_requirement)
        elif isinstance(quest_requirement,Quest_requirement_get_n_skill_points):
            return self.build_get_skill_number_to_n_quest_solver(quest_requirement=quest_requirement)
        elif isinstance(quest_requirement,Quest_requirement_get_n_attribute_points):
            return self.build_get_attribute_number_to_n_quest_solver(quest_requirement=quest_requirement)
        elif isinstance(quest_requirement,Quest_requirement_item_to_hand_work_product_seconds):
            return self.build_work_item_seconds_quest_solver(quest_requirement=quest_requirement)
        elif isinstance(quest_requirement,Quest_requirement_equip_item):
            return self.build_equip_item_quest_solver(quest_requirement = quest_requirement)
        elif isinstance(quest_requirement,Quest_requirement_work_quest_item):
            return self.build_work_for_quest_item_quest_solver(quest_requirement=quest_requirement)
        elif isinstance(quest_requirement,Quest_requirement_sell_item):
            return self.build_sell_to_merchant_solver(quest_requirement= quest_requirement)
        else :
            raise Exception('Unkwnown type of quest requirement')