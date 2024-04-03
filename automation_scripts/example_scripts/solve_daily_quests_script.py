from the_west_inner.requests_handler import requests_handler
from the_west_inner.player_data import Player_data

from the_west_inner.saloon import get_quest_employer_by_key

class QuestIDSuite:
    """
    Represents a suite of quest IDs categorized by difficulty level.
    """
    
    def __init__(self, 
                 easy_quest_id: int,
                 medium_quest_id: int,
                 hard_quest_id: int
                 ) -> None:
        """
        Initializes the QuestIDSuite object.

        Args:
            easy_quest_id (int): The ID of the easy quest.
            medium_quest_id (int): The ID of the medium quest.
            hard_quest_id (int): The ID of the hard quest.
        """
        self.easy_quest_id = easy_quest_id
        self.medium_quest_id = medium_quest_id
        self.hard_quest_id = hard_quest_id
    
    @property
    def easy(self) -> int:
        """int: The ID of the easy quest."""
        return self.easy_quest_id
    
    @property
    def medium(self) -> int:
        """int: The ID of the medium quest."""
        return self.medium_quest_id
    
    @property
    def hard(self) -> int:
        """int: The ID of the hard quest."""
        return self.hard_quest_id
    
    def get_quests(self, reversed: bool = False) -> list[int]:
        """
        Get a list of quest IDs, optionally reversed.

        Args:
            reversed (bool, optional): If True, return the quest IDs in reverse order. Defaults to False.

        Returns:
            list[int]: A list of quest IDs.
        """
        if reversed:
            return [self.hard, self.medium, self.easy]
        return [self.easy, self.medium, self.hard]

REPEATABLE_CRAFTING_QUEST = {
    2: QuestIDSuite(
        easy_quest_id=2043365,
        medium_quest_id=2043369,
        hard_quest_id=2043373
    )
}

def load(handler: requests_handler):
    """
    Load repeatable quests.

    Args:
        handler (requests_handler): The request handler.
    """
    paper_quests = get_quest_employer_by_key(handler=handler, employer_key='paper')
    paper_quests.quest_list

class RepeatableQuestsSolver:
    """
    Solver for repeatable quests.
    """
    
    def __init__(self,
                 handler: requests_handler,
                 player_data: Player_data
                 ) -> None:
        """
        Initializes the RepeatableQuestsSolver object.

        Args:
            handler (requests_handler): The request handler.
            player_data (Player_data): The player data.
        """
        self.handler = handler
        self.player_data = player_data
        self.crafting_id = player_data.profession_id
        self.crafting_quest_data = REPEATABLE_CRAFTING_QUEST
        self._quest_employer = None
    
    @property
    def quest_list(self):
        """
        Get the quest list.

        Returns:
            list: A list of quests.
        """
        # If the quest employer data is not loaded yet, load it
        if self._quest_employer is None:
            self._quest_employer = get_quest_employer_by_key(handler=self.handler, employer_key='paper')
        return self._quest_employer.quest_list
    
    def solve_crafting_quests(self) -> int:
        """
        Solve crafting quests.

        Returns:
            int: The ID of the solved quest.
        """
        # Get the quest suite for the player's crafting profession
        target_quest_suite: QuestIDSuite | None = self.crafting_quest_data.get(self.crafting_id, None)
        # If no quests are available for the player's crafting profession, raise an exception
        if target_quest_suite is None:
            raise Exception('The target repeatable quest stuff is not implemented!')
        
        # Get the list of quest IDs for the crafting profession, in reverse order
        quest_list = target_quest_suite.get_quests(reversed=True)
        
        # Iterate over the quest IDs
        for quest_id in quest_list:
            # Get the quest object from the quest list
            quest = self.quest_list.get_by_id(search_id=quest_id)
            
            # If the quest is not completed, continue to the next quest
            if not quest.is_completed:
                continue
            
            # If the quest is not accepted, accept it
            if not quest.is_accepted:
                quest.accept_quest(handler=self.handler)
            
            # Complete the quest and return its ID
            quest.complete_quest(handler=self.handler)
            return quest_id
        
    def solve_solved_repeatable_quests(self) -> list[int]:
        """
        Solve solved repeatable quests.

        Returns:
            list[int]: A list of solved quest IDs.
        """
        # Get the quest suite for the player's crafting profession
        target_quest_suite: QuestIDSuite | None = self.crafting_quest_data.get(self.crafting_id, QuestIDSuite(None, None, None))
        crafting_quest_list = target_quest_suite.get_quests()
        
        completed_quest_list = []
        # Iterate over the quest list
        for quest in self.quest_list:
            # If the quest is not completed or it's a crafting quest, continue to the next quest
            if not quest.is_completed or quest.quest_id in crafting_quest_list:
                continue
            
            # If the quest is not accepted, accept it
            if not quest.is_accepted:
                quest.accept_quest(handler=self.handler)
            
            # Complete the quest and add its ID to the completed quest list
            quest.complete_quest(handler=self.handler)
            completed_quest_list.append(quest.quest_id)
        
        return completed_quest_list