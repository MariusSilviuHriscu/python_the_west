from the_west_inner.quest_requirements import Quest_requirement_item_to_hand_work_product_seconds
from the_west_inner.game_classes import Game_classes
from the_west_inner.work import get_closest_workplace_data
from the_west_inner.items import get_corresponding_work_id

from automation_scripts.product_work_cycle import CycleJobsProducts



class WorkItemSecondsQuestSolver:
    """
    A class to solve quests that require obtaining a certain number of items through work with a time limit.

    Attributes:
        quest_requirement (Quest_requirement_item_to_hand_work_product_seconds): The quest requirement object.
        game_classes (Game_classes): An object containing various game-related information.
        energy_recharge_id (int): The ID of the energy recharge item used for work.
    """

    def __init__(self,
                 quest_requirement:Quest_requirement_item_to_hand_work_product_seconds,
                 game_classes : Game_classes,
                 energy_recharge_id : int):
        """
        Initializes the WorkItemSecondsQuestSolver.

        Args:
            quest_requirement (Quest_requirement_item_to_hand_work_product_seconds): The quest requirement object.
            game_classes (Game_classes): An object containing various game-related information.
            energy_recharge_id (int): The ID of the energy recharge item used for work.
        """
        self.quest_requirement = quest_requirement
        self.game_classes = game_classes
        self.energy_recharge_id = energy_recharge_id

    def solve(self) -> bool:
        """
        Solves the quest requirement by checking if the required number of items is already in the player's bag.
        If not, the player attempts to acquire the items through work with a time limit.

        Returns:
            bool: True if the quest requirement is solved, False otherwise.
        """
        if self.game_classes.bag[self.quest_requirement.item_id] >= self.quest_requirement.number:
            # If the required number of items is already in the bag, declare the quest requirement as solved
            self.quest_requirement.declare_solved()
            return True

        # Get data for the closest workplace related to the required item
        job_data = get_closest_workplace_data(
            handler=self.game_classes.handler,
            job_id=get_corresponding_work_id(
                id_item=self.quest_requirement.item_id,
                work_list=self.game_classes.work_list
            ),
            job_list=self.game_classes.work_list,
            player_data=self.game_classes.player_data
        )

        # Create a cycle to perform work and acquire the required items
        cycle_products = CycleJobsProducts(
            handler=self.game_classes.handler,
            work_manager=self.game_classes.work_manager,
            consumable_handler=self.game_classes.consumable_handler,
            job_data=job_data,
            player_data=self.game_classes.player_data,
            product_id=self.quest_requirement.item_id,
            game_classes=self.game_classes
        )

        # Set the consumable limit based on the available energy recharge items
        cycle_products.set_consumable_limit(limit_number=self.game_classes.bag[self.energy_recharge_id])

        # Perform the work cycle
        rewards = cycle_products.cycle(
            energy_consumable=self.energy_recharge_id,
            target_number=self.quest_requirement.number - self.game_classes.bag[self.quest_requirement.item_id],
            number_of_task_groups=9 if self.game_classes.premium.automation else 4
        )

        # Add acquired items to the player's bag
        self.game_classes.bag.add_item_dict(item_dict=rewards.item_drop)

        if self.game_classes.bag[self.quest_requirement.item_id] >= self.quest_requirement.number:
            # If the required number of items is now in the bag, declare the quest requirement as solved
            self.quest_requirement.declare_solved()
            return True

        return False