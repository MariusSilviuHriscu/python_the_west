from the_west_inner.quest_requirements import Quest_requirement_item_to_hand_work_product_hourly
from the_west_inner.game_classes import Game_classes
from the_west_inner.crafting import acquire_product


class WorkItemHourlyQuestSolver:
    """
    A class to solve quests that require obtaining a certain number of items through hourly work.

    Attributes:
        quest_requirement (Quest_requirement_item_to_hand_work_product): The quest requirement object.
        game_classes (Game_classes): An object containing various game-related information.
    """

    def __init__(self, quest_requirement:Quest_requirement_item_to_hand_work_product_hourly, game_classes:Game_classes):
        """
        Initializes the WorkItemHourlyQuestSolver.

        Args:
            quest_requirement (Quest_requirement_item_to_hand_work_product): The quest requirement object.
            game_classes (Game_classes): An object containing various game-related information.
        """
        self.quest_requirement = quest_requirement
        self.game_classes = game_classes

    def solve(self) -> bool:
        """
        Solves the quest requirement by checking if the required number of items is already in the player's bag.
        If not, the player attempts to acquire the items through work.

        Returns:
            bool: True if the quest requirement is solved, False otherwise.
        """
        if self.game_classes.bag[self.quest_requirement.item_id] >= self.quest_requirement.number:
            # If the required number of items is already in the bag, declare the quest requirement as solved
            self.quest_requirement.declare_solved()
            return True

        # If not enough items, attempt to acquire the required number through work
        acquire_product(
            id_item=self.quest_requirement.item_id,
            nr=self.quest_requirement.number,
            game_classes=self.game_classes
        )

        return False