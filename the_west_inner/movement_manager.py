import typing

from towns import Town
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
            town = self.map.towns[town]
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

    def move_to_closest_town(self):
        """
        Moves the player to the closest town.

        Returns:
            int: The ID of the town the player moved to.
        """
        town_list = self.map.towns
        closest_town = town_list.get_closest_town(player_data=self.player_data)
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
            map_town = self.map.towns[town]
            coordinates = (map_town.x, map_town.y)
        else:
            raise Exception('Invalid type of input')
        return self.player_data.absolute_distance_to(final_position=coordinates)
