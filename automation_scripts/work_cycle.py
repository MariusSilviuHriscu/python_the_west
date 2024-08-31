import typing

from the_west_inner.game_classes import Game_classes
from the_west_inner.misc_scripts import wait_until_date_callback
from the_west_inner.work_manager import Work_manager
from the_west_inner.work import Work
from the_west_inner.consumable import Consumable_handler
from the_west_inner.reports import Reports_manager

from automation_scripts.sleep_func_callbacks.callback_chain import CallbackChainer

class Script_work_task:
    """
    Handler the logic required for the caracter to do a number of tasks for a certain Work object

    Args:
        work_manager (Work_manager): The manager responsible for handling work tasks.
        work_data (Work): The specific work data for the task.
        number_of_actions (int): The number of work tasks for this work.
        game_classes (Game_classes): The game-related classes and data.

    Attributes:
        work_manager (Work_manager): The manager responsible for handling work tasks.
        work_data (Work): The specific work data for the task.
        number_of_actions (int): The remaining number of actions to perform for this task.
        game_classes (Game_classes): The game-related classes and data.
    """

    def __init__(self, work_manager: Work_manager, work_data: Work, number_of_actions: int, game_classes: Game_classes):
        self.work_manager = work_manager
        self.work_data = work_data
        self.number_of_actions = number_of_actions
        self.game_classes = game_classes

    def execute(self ,callback_function : typing.Callable[...,None]=None, *args, **kwargs):
        """
        Execute the work task by performing actions until the number_of_actions reaches zero.
        """
        while self.number_of_actions != 0:
            # Wait until the task queue is empty .
            wait_until_date_callback(
                            wait_time = self.game_classes.task_queue.get_tasks_expiration(),
                            handler = self.game_classes.handler,
                            callback_function = callback_function,
                            *args ,
                            **kwargs
                            )

            # Determine the maximum number of tasks allowed
            maximum_number_of_task_allowed = self.work_manager.allowed_tasks()

            # Perform the work for the minimum of maximum allowed tasks and remaining actions
            self.work_manager.work(work_object=self.work_data, number_of_tasks=min(maximum_number_of_task_allowed, self.number_of_actions))

            # Reduce the remaining actions
            self.number_of_actions -= min(maximum_number_of_task_allowed, self.number_of_actions)

        # Wait for the task's expiration time again when the execution of the method is done.
        wait_until_date_callback(
                            wait_time = self.game_classes.task_queue.get_tasks_expiration(),
                            handler = self.game_classes.handler,
                            callback_function = callback_function,
                            *args ,
                            **kwargs
                            )

#def read_report_rewards(report_manager:Reports_manager):
#            report_manager._read_reports(retry_times=3)
#            print(f'succesful reading of reports : {report_manager.rewards}')

class Cycle_jobs:
    """
    Is an object that handles the logic of working jobs and replenishing energy and motivation .

    Args:
        game_classes (Game_classes): The game-related classes and data.
        job_data (List[Work]): List of work data representing the targeted jobs.
        consumable_handler (Consumable_handler): Handler for consumable items.

    Attributes:
        handler (Handler): The handler for game-related actions.
        job_data (List[Work]): List of work data representing target jobs.
        game_classes (Game_classes): The game-related classes and data.
        work_manager (Work_manager): The manager responsible for handling work tasks.
        consumable_handler (Consumable_handler): Handler for consumable items.
    """

    def __init__(self, game_classes: Game_classes, job_data: typing.List[Work], consumable_handler: Consumable_handler):
        self.handler = game_classes.handler
        self.job_data = job_data
        self.game_classes = game_classes
        self.work_manager = game_classes.work_manager
        self.consumable_handler = consumable_handler
        self.reports_manager = Reports_manager(handler=self.handler)
        self.work_callback_chainer = None
        self.consumable_callback_chainer = None
    
    
    def update_work_callback_chainer(self,callback_chain : CallbackChainer):
        self.work_callback_chainer = callback_chain
    
    def get_work_callback_function(self) -> typing.Callable | None:
        if self.work_callback_chainer is None:
            return None
        return self.work_callback_chainer.chain_function(report_manager = self.report_manager)
    
    def update_consumable_callback_chainer(self,callback_chain:CallbackChainer):
        self.consumable_callback_chainer = callback_chain
    
    def get_consumable_callback_function(self) -> typing.Callable | None:
        if self.consumable_callback_chainer is None:
            return None
        return self.consumable_callback_chainer.chain_function(report_manager = self.report_manager)
    def _analize_motivation(self) -> typing.List[Script_work_task]:
        """
        Analyze motivation levels and create a list of Script_work_task objects based on available actions.

        Returns:
            List[Script_work_task]: List of work tasks to be executed.
        """
        player_data = self.game_classes.player_data
        player_data.update_character_variables(self.handler)
        energy = player_data.energy
        motivation = self.game_classes.work_list.motivation(self.handler)
        work_tasks_actions = []
        possible_actions = energy

        # Loop through available jobs and motivation levels
        for job in self.job_data:
            if motivation[str(job.job_id)] > 75 and possible_actions != 0:
                actions = min(motivation[str(job.job_id)] - 75, possible_actions)
                possible_actions -= actions

                # Create Script_work_task object with work details
                work_tasks_actions.append(Script_work_task(work_manager=self.work_manager, work_data=job, number_of_actions=actions, game_classes=self.game_classes))

            if possible_actions == 0:
                break

        return work_tasks_actions

    def work_cycle(self, motivation_consumable: int):
        """
        Execute the work tasks cycle based on available motivation and energy.

        Args:
            motivation_consumable (int): The ID of the motivation consumable item.
        """
        work_data = self._analize_motivation()

        if len(work_data) == 0:
            return True
        
        # Execute work tasks in the cycle
        for work_task in work_data:
            work_task.execute(callback_function = self.get_work_callback_function())

        self.reports_manager._read_reports(retry_times=3)
        
        # Recursive call to continue the cycle
        return self.work_cycle(motivation_consumable=motivation_consumable)

    def cycle(self, motivation_consumable: int, energy_consumable: int, number_of_cycles=1):
        """
        Execute the work cycle for a specified number of cycles.

        Args:
            motivation_consumable (int): The ID of the motivation consumable item.
            energy_consumable (int): The ID of the energy consumable item.
            number_of_cycles (int, optional): Number of cycles to perform. Defaults to 1.
        """
        player_data = self.game_classes.player_data
        initial_number_of_cycles = number_of_cycles
        player_data = self.game_classes.player_data
        player_data.update_character_variables(self.handler)
        energy = player_data.energy

        # Use energy consumable if energy is low in the first cycle
        if energy <= 2 and number_of_cycles == 1:
            self.consumable_handler.use_consumable(consumable_id = energy_consumable,
                                                   function_callback = self.get_consumable_callback_function()
                                                   )
            player_data.update_character_variables(self.handler)

        # Execute work cycles
        while number_of_cycles != 0:
            if energy <= 2 and initial_number_of_cycles == 1:
                break

            if energy <= 2:
                # Use energy consumable to continue cycling
                self.consumable_handler.use_consumable(consumable_id = energy_consumable,
                                                   function_callback = self.get_consumable_callback_function()
                                                   )
                player_data.update_character_variables(self.handler)
                number_of_cycles -= 1

            # Execute the work cycle and update energy
            solution = self.work_cycle(motivation_consumable=motivation_consumable)
            player_data = self.game_classes.player_data
            player_data.update_character_variables(self.handler)
            energy = player_data.energy

            # Use motivation consumable if cycle was successful and energy is sufficient
            if solution and energy >= 3:
                self.consumable_handler.use_consumable(consumable_id = motivation_consumable,
                                                   function_callback = self.get_consumable_callback_function()
                                                   )
        return self.reports_manager.rewards