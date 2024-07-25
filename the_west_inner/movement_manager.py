import typing

from map import MapLoader
from towns import Town,Town_list
from task_queue import TaskQueue
from work_manager import Work_manager
from misc_scripts import wait_until_date
from requests_handler import requests_handler
from player_data import Player_data

class MovementManager:
    """
    Class to manage movement-related tasks for the player.

    Attributes:
        handler (requests_handler): The request handler object.
        task_queue (TaskQueue): The task queue object.
        work_manager (Work_manager): The work manager object.
        player_data (Player_data): The player data object.
    """
    def __init__(self,
                 handler: requests_handler,
                 task_queue: TaskQueue,
                 work_manager: Work_manager,
                 player_data: Player_data):
        """
        Initializes the MovementManager.

        Args:
            handler (requests_handler): The request handler object.
            task_queue (TaskQueue): The task queue object.
            work_manager (Work_manager): The work manager object.
            player_data (Player_data): The player data object.
        """
        self.handler = handler
        self.task_queue = task_queue
        self.work_manager = work_manager
        self.player_data = player_data
        self._town_list : None|Town_list = None
    @property
    def town_list(self) -> Town_list:
        if self._town_list:
            return self._town_list
        
        loader = MapLoader(
            handler = self.handler,
            player_data = self.player_data,
            work_list = None
        )
        
        self._town_list = loader.get_town_list()
        
        return self._town_list
    def check_location(self, target_x: int, target_y: int) -> bool:
        """
        Checks if the player is at the specified location.

        Args:
            target_x (int): The x-coordinate of the target location.
            target_y (int): The y-coordinate of the target location.

        Returns:
            bool: True if the player is at the specified location, False otherwise.
        """
        return self.player_data.x == target_x and self.player_data.y == target_y

    def move_to_town(self, town: int | Town):
        """
        Moves the player to the specified town.

        Args:
            town (int or Town): The ID or instance of the target town.

        Returns:
            int: The ID of the town the player moved to.
        """
        if isinstance(town, Town):
            return self._move_to_town(town=town)
        elif isinstance(town, int) or isinstance(town, str):
            town = self.town_list[town]
            return self._move_to_town(town=town)

    def _move_to_town(self, town: Town) -> int:
        """
        Moves the player to the specified town (internal method).

        Args:
            town (Town): The instance of the target town.

        Returns:
            int: The ID of the town the player moved to.
        """
        if self.check_location(target_x=town.x, target_y=town.y):
            return town.town_id
        self.work_manager.move_to_town(town_id=town.town_id)
        wait_until_date(wait_time=self.task_queue.get_tasks_expiration(), handler=self.handler)
        self.player_data.update_visible_variables(handler=self.handler)
        return town.town_id

    def move_to_closest_town(self , key : typing.Callable[[Town], bool] | None = None) :
        """
        Moves the player to the closest town.

        Returns:
            int: The ID of the town the player moved to.
        """
        
        closest_town = self.town_list.get_closest_town(player_data=self.player_data , key= key)
        if closest_town is None:
            raise Exception('No town matching your requirement has been found !')
        return self.move_to_town(town=closest_town)

    def get_distance_to_town(self, town: int | Town) -> int | float:
        """
        Calculates the distance to the specified town.

        Args:
            town (int or Town): The ID or instance of the target town.

        Returns:
            int or float: The distance to the specified town.
        """
        if isinstance(town, Town):
            coordinates = (town.x, town.y)
        elif isinstance(town, int) or isinstance(town, str):
            map_town = self.town_list[town]
            coordinates = (map_town.x, map_town.y)
        else:
            raise Exception('Invalid type of input')
        return self.player_data.absolute_distance_to(final_position=coordinates)
