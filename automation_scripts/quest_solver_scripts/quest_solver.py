from typing import Protocol

from the_west_inner.quest_requirements import (
                                                Quest_requirement_travel,
                                                Quest_requirement_item_to_hand_work_product,
                                                Quest_requirement_item_to_hand_buy_from_marketplace
                                                )

from the_west_inner.game_classes import Game_classes
from the_west_inner.work import get_closest_workplace_data
from the_west_inner.items import Items,get_corresponding_work_id
from the_west_inner.bag import Bag
from the_west_inner.work_manager import Work_manager
from the_west_inner.marketplace_buy import Marketplace_buy_manager
from the_west_inner.marketplace_pickup_manager import MarketplacePickupManager
from the_west_inner.crafting import acquire_product

from automation_scripts.work_cycle import Script_work_task
from automation_scripts.product_work_cycle import CycleJobsProducts

class QuestSolver(Protocol):
    """
    A protocol representing the interface for quest solvers.

    Methods:
        solve() -> bool:
            Attempt to solve the quest and return True if successful, False otherwise.
    """

    def solve(self) -> bool:
        """
        Attempt to solve the quest.

        Returns:
            bool: True if the quest is successfully solved, False otherwise.
        """
        pass



class TravelQuestSolver:
    """
    A class to solve quests that require traveling to a specific location.

    Attributes:
        travel_quest_requirement (Quest_requirement_travel): The quest requirement object.
        work_manager (Work_manager): The manager for handling work-related actions.
    """

    def __init__(self, travel_quest_requirement, work_manager):
        """
        Initializes the TravelQuestSolver.

        Args:
            travel_quest_requirement (Quest_requirement_travel): The quest requirement object.
            work_manager (Work_manager): The manager for handling work-related actions.
        """
        self.travel_quest_requirement = travel_quest_requirement
        self.work_manager = work_manager

    def solve(self) -> bool:
        """
        Solves the travel quest requirement by moving the player to the specified location.

        Returns:
            bool: True if the travel quest requirement is solved, False otherwise.
        """
        # Move to the quest employer's location
        self.work_manager.move_to_quest_employer(
            quest_employer_key=self.travel_quest_requirement.employer_key,
            x=self.travel_quest_requirement.x,
            y=self.travel_quest_requirement.y
        )

        # Wait until the work queue is free
        self.work_manager.wait_until_free_queue()

        # Declare the travel quest requirement as solved
        self.travel_quest_requirement.declare_solved()

        return True


class WorkItemHourlyQuestSolver:
    """
    A class to solve quests that require obtaining a certain number of items through hourly work.

    Attributes:
        quest_requirement (Quest_requirement_item_to_hand_work_product): The quest requirement object.
        game_classes (Game_classes): An object containing various game-related information.
    """

    def __init__(self, quest_requirement, game_classes):
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


class WorkItemSecondsQuestSolver:
    """
    A class to solve quests that require obtaining a certain number of items through work with a time limit.

    Attributes:
        quest_requirement (Quest_requirement_item_to_hand_work_product): The quest requirement object.
        game_classes (Game_classes): An object containing various game-related information.
        energy_recharge_id (int): The ID of the energy recharge item used for work.
    """

    def __init__(self, quest_requirement, game_classes, energy_recharge_id):
        """
        Initializes the WorkItemSecondsQuestSolver.

        Args:
            quest_requirement (Quest_requirement_item_to_hand_work_product): The quest requirement object.
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


class MarketplaceItemQuestSolver():
    """
    A class to solve quests that require buying items from the marketplace.

    Attributes:
        quest_requirement (Quest_requirement_item_to_hand_buy_from_marketplace): The quest requirement object.
        marketplace_buy_manager (Marketplace_buy_manager): The manager for buying items from the marketplace.
        marketplace_pickup_manager (MarketplacePickupManager): The manager for picking up items bought from the marketplace.
        bag (Bag): The bag object representing the player's inventory.
    """

    def __init__(self, quest_requirement, marketplace_buy_manager, marketplace_pickup_manager, bag):
        """
        Initializes the MarketplaceItemQuestSolver.

        Args:
            quest_requirement (Quest_requirement_item_to_hand_buy_from_marketplace): The quest requirement object.
            marketplace_buy_manager (Marketplace_buy_manager): The manager for buying items from the marketplace.
            marketplace_pickup_manager (MarketplacePickupManager): The manager for picking up items bought from the marketplace.
            bag (Bag): The bag object representing the player's inventory.
        """
        self.quest_requirement = quest_requirement
        self.marketplace_buy_manager = marketplace_buy_manager
        self.marketplace_pickup_manager = marketplace_pickup_manager
        self.bag = bag

    def solve(self) -> bool:
        """
        Solves the quest requirement by buying the required items from the marketplace.

        Returns:
            bool: True if the quest requirement is solved, False otherwise.
        """
        # Buy the required number of items from the marketplace
        number_bought = self.marketplace_buy_manager.buy_cheapest_n_items(
            item_id=self.quest_requirement.item_id,
            item_number=self.quest_requirement.number,
            buy_anyway=True
        )

        if number_bought == self.quest_requirement.number:
            # If successfully bought, fetch all bought items from the marketplace
            self.marketplace_pickup_manager.fetch_all_bought()
            # Declare the quest requirement as solved
            self.quest_requirement.declare_solved()
            return True

        return False