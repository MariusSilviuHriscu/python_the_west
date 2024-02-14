from the_west_inner.quest_requirements import Quest_requirement_travel
from the_west_inner.work_manager import Work_manager

class TravelQuestSolver:
    """
    A class to solve quests that require traveling to a specific location.

    Attributes:
        travel_quest_requirement (Quest_requirement_travel): The quest requirement object.
        work_manager (Work_manager): The manager for handling work-related actions.
    """

    def __init__(self, travel_quest_requirement : Quest_requirement_travel , work_manager : Work_manager):
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