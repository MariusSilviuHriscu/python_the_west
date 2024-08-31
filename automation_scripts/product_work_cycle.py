import typing

from automation_scripts.work_cycle import Script_work_task

from the_west_inner.requests_handler import requests_handler
from the_west_inner.game_classes import Game_classes
from the_west_inner.work_manager import Work_manager
from the_west_inner.player_data import Player_data
from the_west_inner.work import Work
from the_west_inner.consumable import Consumable_handler
from the_west_inner.reports import Reports_manager


from automation_scripts.sleep_func_callbacks.callback_chain import CallbackChainer

class CycleJobsProducts:
    """
    A class representing the cycle of jobs and product acquisition in the game.

    Attributes:
        handler (requests_handler): The requests handler for making game-related requests.
        work_manager (Work_manager): The manager for handling work-related actions.
        consumable_handler (Consumable_handler): The manager for handling consumable items.
        job_data (Work): Data representing the specific work/job for the cycle.
        player_data (Player_data): Data representing the player's character.
        product_id (int): The ID of the product to be acquired during the cycle.
        game_classes (Game_classes): An object containing various game-related information.
        report_manager (Reports_manager): The manager for handling game reports.
        used_energy_consumable (int | None): The number of energy consumables used during the cycle.
        work_callback_chainer (CallbackChainer): Chain of callback functions for work-related actions.
        consumable_callback_chainer (CallbackChainer): Chain of callback functions for consumable actions.
    """

    def __init__(self,
                 handler: requests_handler,
                 work_manager: Work_manager,
                 consumable_handler: Consumable_handler,
                 job_data: Work,
                 player_data: Player_data,
                 product_id: int,
                 game_classes: Game_classes
                 ):
        self.handler = handler
        self.work_manager = work_manager
        self.consumable_handler = consumable_handler
        self.job_data = job_data
        self.player_data = player_data
        self.product_id = product_id
        self.game_classes = game_classes
        self.report_manager = Reports_manager(handler=handler)
        self.used_energy_consumable: int | None = None
        self.work_callback_chainer = None
        self.consumable_callback_chainer = None

    def set_consumable_limit(self, limit_number: int = 0):
        """
        Set the limit on the number of energy consumables to be used during the cycle.

        Args:
            limit_number (int): The limit on the number of energy consumables.
        """
        self.used_energy_consumable = limit_number

    def update_work_callback_chainer(self, callback_chain: CallbackChainer):
        """
        Update the chain of callback functions for work-related actions.

        Args:
            callback_chain (CallbackChainer): Chain of callback functions for work-related actions.
        """
        self.work_callback_chainer = callback_chain

    def get_work_callback_function(self) -> typing.Callable | None:
        """
        Get the callback function for work-related actions.

        Returns:
            typing.Callable | None: The callback function for work-related actions.
        """
        if self.work_callback_chainer is None:
            return None
        return self.work_callback_chainer.chain_function(report_manager=self.report_manager)

    def update_consumable_callback_chainer(self, callback_chain: CallbackChainer):
        """
        Update the chain of callback functions for consumable actions.

        Args:
            callback_chain (CallbackChainer): Chain of callback functions for consumable actions.
        """
        self.consumable_callback_chainer = callback_chain

    def get_consumable_callback_function(self) -> typing.Callable | None:
        """
        Get the callback function for consumable actions.

        Returns:
            typing.Callable | None: The callback function for consumable actions.
        """
        if self.consumable_callback_chainer is None:
            return None
        return self.consumable_callback_chainer.chain_function(report_manager=self.report_manager)

    def _recharge_energy(self, energy_consumable: int):
        """
        Recharge energy using a consumable.

        Args:
            energy_consumable (int): The ID of the energy consumable to be used.
        """
        self.consumable_handler.use_consumable(consumable_id=energy_consumable,
                                               function_callback=self.get_consumable_callback_function())
        self.player_data.update_character_variables(handler=self.handler)

    def _recharge_by_actions(self, energy_consumable:int, actions: int):
        """
        Recharge energy based on the available actions.

        Args:
            energy_consumable (int): The ID of the energy consumable to be used.
            actions (int): The number of available actions.

        Returns:
            int: The remaining number of actions after recharging.
        """
        if actions < 0:
            raise ValueError("Number of actions cannot be smaller than 0")

        if actions == 0 and self.used_energy_consumable is None:
            return actions

        if actions == 0 and self.used_energy_consumable != 0:
            self._recharge_energy(energy_consumable=energy_consumable)
            self.used_energy_consumable -= 1
            return self.player_data.energy

        return actions

    def cycle_one_by_one(self, energy_consumable: int, target_number: int):
        """
        
        Perform a cycle of work and product acquisition one action at a time.
    
        Args:
            energy_consumable (int): The ID of the energy consumable to be used.
            target_number (int): The target number of products to be acquired.
    
        Returns:
            dict: The rewards obtained during the cycle.
        """
        # Initialize the counter for dropped items.
        dropped_items = 0
        
        # Recharge energy based on available actions.
        possible_actions = self._recharge_by_actions(energy_consumable=energy_consumable,
                                                    actions=self.player_data.energy)
    
        # Loop until the target number of items is reached.
        while dropped_items < target_number:
            # Create a Script_work_task for a single action.
            work_task = Script_work_task(
                work_manager=self.work_manager,
                work_data=self.job_data,
                number_of_actions=1,
                game_classes=self.game_classes
            )
    
            # Execute the work task.
            work_task.execute()
    
            # Update the remaining actions after consuming one.
            possible_actions = self._recharge_by_actions(energy_consumable=energy_consumable,
                                                        actions=possible_actions - 1)
    
            # Read the reports to get rewards.
            cycle_reward = self.report_manager._read_reports(retry_times=3)
    
            # Update the dropped items counter with the current cycle's drop.
            dropped_items = cycle_reward.item_drop.get(self.product_id, 0)
    
            # Check if no more actions are available.
            if possible_actions == 0:
                return self.report_manager.rewards
        
        # Return the rewards obtained during the entire cycle.
        return self.report_manager.rewards

    def cycle(self, energy_consumable: int, target_number: int, number_of_task_groups: int = 9):
        """
        Perform a cycle of work and product acquisition.
    
        Args:
            energy_consumable (int): The ID of the energy consumable to be used.
            target_number (int): The target number of products to be acquired.
            number_of_task_groups (int): The number of task groups to be used in each cycle.
    
        Returns:
            dict: The rewards obtained during the cycle.
        """
        # Initialize the counter for dropped items.
        dropped_items = 0
        
        # Recharge energy based on available actions.
        possible_actions = self._recharge_by_actions(energy_consumable=energy_consumable,
                                                    actions=self.player_data.energy)
    
        # Loop until the target number of items is reached.
        while dropped_items < target_number:
            # Determine the number of tasks to perform in the current cycle.
            tasks = min(number_of_task_groups, possible_actions)
    
            # Create a Script_work_task for the determined number of tasks.
            work_task = Script_work_task(
                work_manager=self.work_manager,
                work_data=self.job_data,
                number_of_actions=tasks,
                game_classes=self.game_classes
            )
    
            # Execute the work task.
            work_task.execute(callback_function=self.get_work_callback_function())
    
            # Update the remaining actions after consuming tasks.
            possible_actions = self._recharge_by_actions(energy_consumable=energy_consumable,
                                                        actions=possible_actions - tasks)
    
            # Read the reports to get rewards.
            self.report_manager._read_reports(retry_times=3)
    
            # Print the difference in dropped items if it occurs.
            if dropped_items != self.report_manager.rewards.item_drop.get(self.product_id, 0):
                print(f'we dropped {self.report_manager.rewards.item_drop.get(self.product_id, 0) - dropped_items}')
    
            # Update the dropped items counter with the current cycle's drop.
            dropped_items = self.report_manager.rewards.item_drop.get(self.product_id, 0)
    
            # Check if no more actions are available.
            if possible_actions == 0:
                return self.report_manager.rewards
        
        # Return the rewards obtained during the entire cycle.
        return self.report_manager.rewards

