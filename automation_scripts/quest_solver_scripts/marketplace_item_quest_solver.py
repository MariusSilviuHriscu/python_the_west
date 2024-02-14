from the_west_inner.quest_requirements import Quest_requirement_item_to_hand_buy_from_marketplace
from the_west_inner.marketplace_buy import Marketplace_buy_manager
from the_west_inner.marketplace_pickup_manager import MarketplacePickupManager
from the_west_inner.bag import Bag

class MarketplaceItemQuestSolver():
    """
    A class to solve quests that require buying items from the marketplace.

    Attributes:
        quest_requirement (Quest_requirement_item_to_hand_buy_from_marketplace): The quest requirement object.
        marketplace_buy_manager (Marketplace_buy_manager): The manager for buying items from the marketplace.
        marketplace_pickup_manager (MarketplacePickupManager): The manager for picking up items bought from the marketplace.
        bag (Bag): The bag object representing the player's inventory.
    """

    def __init__(self,
                 quest_requirement : Quest_requirement_item_to_hand_buy_from_marketplace,
                 marketplace_buy_manager : Marketplace_buy_manager,
                 marketplace_pickup_manager : MarketplacePickupManager,
                 bag : Bag
                 ):
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