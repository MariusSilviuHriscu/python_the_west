import typing

from the_west_inner.task_queue import TaskQueue, Task_list
from the_west_inner.work_manager import Work_manager
from the_west_inner.requests_handler import requests_handler
from the_west_inner.player_data import Player_data
from the_west_inner.misc_scripts import sleep_closest_town

from automation_scripts.exp_gain_script.exp_script import ExpScript

class CycleSleeperManager:
    """
    Manages the sleeping cycle of a player in the game. Determines when the player can sleep, initiates sleep, 
    and cancels sleep if necessary based on the player's energy level and the task queue status.

    Attributes:
        handler (requests_handler): An instance to handle game requests.
        task_queue (TaskQueue): An instance to manage the task queue.
        work_manager (Work_manager): An instance to manage work-related tasks.
        player_data (Player_data): An instance to manage player-related data.
    """
    
    def __init__(self,
                 handler: requests_handler,
                 task_queue: TaskQueue,
                 work_manager: Work_manager,
                 player_data: Player_data):
        """
        Initializes the CycleSleeperManager with the necessary game components.

        Args:
            handler (requests_handler): An instance to handle game requests.
            task_queue (TaskQueue): An instance to manage the task queue.
            work_manager (Work_manager): An instance to manage work-related tasks.
            player_data (Player_data): An instance to manage player-related data.
        """
        self.handler = handler
        self.task_queue = task_queue
        self.work_manager = work_manager
        self.player_data = player_data

    def check_if_can_sleep(self) -> bool:
        """
        Checks if the player can initiate sleep. The player can sleep if there are no tasks in the task queue 
        and no sleep task is already in the queue.

        Returns:
            bool: True if the player can sleep, False otherwise.
        """
        return self.task_queue.get_tasks_number() == 0 and not self.task_queue.sleep_task_in_queue()

    def _sleep(self):
        """
        Initiates the sleep process by calling the sleep_closest_town function.
        """
        sleep_closest_town(self.handler, self.player_data)
        print('Sleeping')

    def check_if_can_cancel_sleep(self) -> bool:
        """
        Checks if the player can cancel sleep. The player can cancel sleep if their current energy is equal to 
        their maximum energy.

        Returns:
            bool: True if the player can cancel sleep, False otherwise.
        """
        return self.player_data.energy == self.player_data.energy_max

    def _cancel_sleep(self):
        """
        Cancels any sleep task in the task queue.
        """
        if not self.task_queue.sleep_task_in_queue():
            return
        task_list = self.task_queue.return_tasks_by_type(task_type='sleep')
        task_list.cancel()

    def finish_cycle(self):
        """
        Completes the current cycle by initiating sleep if the player can sleep.
        """
        if self.check_if_can_sleep():
            self._sleep()

    def start_cycle(self, exp_script: ExpScript = None) -> bool:
        """
        Starts a new cycle by checking if a sleep task can be cancelled or if there is no sleep task in the queue. 
        If either condition is met, it cancels the sleep task and returns True, indicating the cycle can start.

        Args:
            exp_script (ExpScript, optional): An optional experience script to check for experience thresholds.

        Returns:
            bool: True if the cycle can start, False otherwise.
        """
        if exp_script is not None:
            # Check if the experience from the script exceeds the level experience requirement
            actions = exp_script.get_script_actions()
            if actions.calc_exp() > self.player_data.exp_data.level_exp_requirement:
                self._cancel_sleep()
                print('The experience from the script exceeds the level experience requirement. Canceled sleep.')
                return True
            
        if not self.task_queue.sleep_task_in_queue() or self.check_if_can_cancel_sleep():
            print('Cancelling sleep.')
            self._cancel_sleep()
            return True
        return False
