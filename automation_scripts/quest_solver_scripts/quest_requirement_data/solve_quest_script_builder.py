import typing
from automation_scripts.quest_solver_scripts.quest_requirement_data.quest_group_data import QuestGroupData
from the_west_inner.game_classes import Game_classes

from automation_scripts.quest_solver_scripts.quest_solver_manager import build_quest_group_solver_manager


def build_solver_executable(quest_group_data :QuestGroupData) -> typing.Callable[[Game_classes],bool]:
    
    def executable(game_data : Game_classes) -> bool:
        
        manager = build_quest_group_solver_manager(
            game_classes= game_data,
            target_quest_group_data = quest_group_data
        )
        return manager.solve()
    return executable