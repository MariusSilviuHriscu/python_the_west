from typing import Protocol




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
