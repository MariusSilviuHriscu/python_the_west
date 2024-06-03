import typing

from the_west_inner.game_classes import Game_classes
from the_west_inner.player_data import Player_data
from the_west_inner.work import Work
from the_west_inner.map import Map

from the_west_inner.work_job_data import (WorkDataLoader,
                                          WorkJobDataManager,
                                          WorkSortRule,
                                          WorkValidationRule,
                                          WorkJobData,
                                          WorkData
                                          )

from automation_scripts.work_cycle import Script_work_task

from automation_scripts.stop_events.script_exception_handler import handle_exceptions

class ExpScriptJobDataManager:
    """
    Manages work data, sorting rules, and validation rules for work tasks.
    
    Attributes:
        work_data_loader (WorkDataLoader): The loader for work data.
        work_sort_rule_list (list[WorkSortRule]): List of rules for sorting work.
        work_validation_rule_list (list[WorkValidationRule]): List of rules for validating work.
    """

    def __init__(self,
                 work_data_loader: WorkDataLoader,
                 work_sort_rule_list: list[WorkSortRule],
                 work_validation_rule_list: list[WorkValidationRule]
                 ):
        """
        Initializes the ExpScriptJobDataManager with provided data and rules.

        Args:
            work_data_loader (WorkDataLoader): Loader for work data.
            work_sort_rule_list (list[WorkSortRule]): List of rules for sorting work.
            work_validation_rule_list (list[WorkValidationRule]): List of rules for validating work.
        """
        self.work_data_loader = work_data_loader
        self.work_sort_rule_list = work_sort_rule_list
        self.work_validation_rule_list = work_validation_rule_list

    def _get_job_data_manager(self):
        """
        Private method to get the job data manager from the loader.
        
        Returns:
            WorkJobDataManager: Instance of WorkJobDataManager.
        """
        return self.work_data_loader.get_work_data_manager()

    @property
    def job_data_manager(self) -> WorkJobDataManager:
        """
        Property to access the job data manager.
        
        Returns:
            WorkJobDataManager: Instance of WorkJobDataManager.
        """
        return self._get_job_data_manager()

    def get_filtered_job_data(self) -> list[WorkJobData]:
        """
        Get filtered and sorted work job data based on defined rules.
        
        Returns:
            list[WorkJobData]: Filtered and sorted list of work job data.
        """
        return self.job_data_manager.sort_by_work_sort_rule(
            work_sort_rules=self.work_sort_rule_list,
            filter_rules=self.work_validation_rule_list,
        )



class ExpScriptAction:
    """
    Represents an action in the ExpScript, including the number of actions, duration, and associated work job data.

    Attributes:
        action_number (int): Number of actions to perform.
        duration (int): Duration of each action.
        job_data (WorkJobData): Associated work job data for the action.
    """

    def __init__(self, action_number: int, duration: int, job_data: WorkJobData):
        """
        Initializes an ExpScriptAction object with provided data.

        Args:
            action_number (int): Number of actions to perform.
            duration (int): Duration of each action.
            job_data (WorkJobData): Associated work job data for the action.
        """
        self.action_number = action_number
        self.duration = duration
        self.job_data = job_data
    
    def calc_exp(self) -> int:
        """
        Calculates the total experience gained from the action.
        
        Returns:
            int: Total experience gained.
        """
        work_data: WorkData = self.job_data.timed_work_data[self.duration]
        return work_data.xp * self.action_number
    
    def calc_worktime(self) -> int:
        """
        Calculates the total work time for the action.
        
        Returns:
            int: Total work time.
        """
        return self.duration * self.action_number

    def __str__(self) -> str:
        """
        Returns a string representation of the ExpScriptAction object.
        
        Returns:
            str: String representation.
        """
        return f'ExpScriptAction(action_number={self.action_number}, duration={self.duration}, job_data={self.job_data})'
    
    def __repr__(self) -> str:
        """
        Returns a string representation of the ExpScriptAction object.
        
        Returns:
            str: String representation.
        """
        return self.__str__()

    
class ExpScriptActionList:
    """
    Represents a list of ExpScriptAction objects.

    Attributes:
        exp_action_list (list[ExpScriptAction]): List of ExpScriptAction objects.
    """

    def __init__(self, exp_action_list: list[ExpScriptAction] | None = None):
        """
        Initializes an ExpScriptActionList object.

        Args:
            exp_action_list (list[ExpScriptAction], optional): List of ExpScriptAction objects. Defaults to None.
        """
        self.exp_action_list = exp_action_list or []

    def append(self, exp_action: ExpScriptAction):
        """
        Appends an ExpScriptAction to the list.

        Args:
            exp_action (ExpScriptAction): ExpScriptAction to append.
        """
        self.exp_action_list.append(exp_action)
    
    def calc_exp(self) -> int:
        """
        Calculates the total experience gained from all actions in the list.

        Returns:
            int: Total experience gained.
        """
        return sum([x.calc_exp() for x in self.exp_action_list])
    
    def calc_worktime(self) -> int:
        """
        Calculates the total work time for all actions in the list.

        Returns:
            int: Total work time.
        """
        return sum([x.calc_worktime() for x in self.exp_action_list])
    
    def copy(self) -> typing.Self:
        """
        Creates a copy of the ExpScriptActionList.

        Returns:
            typing.Self: Copy of the ExpScriptActionList.
        """
        return ExpScriptActionList(
            exp_action_list=[ExpScriptAction(
                action_number=x.action_number,
                duration=x.duration,
                job_data=x.job_data
            ) for x in self.exp_action_list]
        )
    
    def __iter__(self) -> typing.Iterator[ExpScriptAction]:
        """
        Returns an iterator over the ExpScriptAction objects in the list.

        Returns:
            typing.Iterator[ExpScriptAction]: Iterator over ExpScriptAction objects.
        """
        return iter(self.exp_action_list)
    
    def pop_last_action_number(self):
        """
        Decreases the action number of the last action in the list by 1, and removes it if it becomes 0.
        """
        if self.exp_action_list:
            last_action = self.exp_action_list[-1]
            last_action.action_number -= 1
            if last_action.action_number == 0:
                self.exp_action_list.pop()
    
    def filter_to_exp_target(self, exp_target: int) -> None:
        """
        Filters the action list to meet a target experience value, adjusting action numbers accordingly.

        Args:
            exp_target (int): Target experience value.
        """
        if self.calc_exp() < exp_target or len(self.exp_action_list) == 0:
            return 
        
        practice_action_list = self.copy()
        
        practice_action_list.pop_last_action_number()
        
        while exp_target < practice_action_list.calc_exp() and len(self.exp_action_list) != 0:
            self.pop_last_action_number()
            practice_action_list.pop_last_action_number()

    def __len__(self) -> int:
        """
        Returns the total number of actions in the list.

        Returns:
            int: Total number of actions.
        """
        return sum([x.action_number for x in self.exp_action_list])
    
    def __str__(self) -> str:
        """
        Returns a string representation of the ExpScriptActionList.

        Returns:
            str: String representation.
        """
        return f'{self.exp_action_list}'

            
class ExpScriptJobSelector:
    """
    Selects jobs for the ExpScript based on available motivation and energy.

    Attributes:
        duration (int): Duration of each action.
        player_data (Player_data): Player data containing energy and other relevant information.
    """

    def __init__(self, duration: int, player_data: Player_data):
        """
        Initializes an ExpScriptJobSelector object.

        Args:
            duration (int): Duration of each action.
            player_data (Player_data): Player data containing energy and other relevant information.
        """
        self.duration = duration
        self.player_data = player_data

    def get_possible_action_list(self, work_job_data: list[WorkJobData], duration: int) -> ExpScriptActionList:
        """
        Generates a list of possible ExpScriptActions based on available motivation and energy.

        Args:
            work_job_data (list[WorkJobData]): List of available work job data.
            duration (int): Duration of each action.

        Returns:
            ExpScriptActionList: List of possible ExpScriptActions.
        """
        # Initialize an empty list to store the possible actions
        job_target_data = ExpScriptActionList()
        # Initialize the remaining energy from the player's data
        actions = self.player_data.energy

        # Iterate over each work job data
        for job in work_job_data:
            # Calculate the maximum number of actions the player can perform for this job based on motivation and energy
            possible_actions = job.motivation * 100 - 75

            # If the possible actions are non-positive, skip this job
            if possible_actions <= 0:
                continue

            # Create an ExpScriptAction object with the calculated number of actions, duration, and job data
            script_action = ExpScriptAction(
                action_number=int(min(possible_actions, actions)),
                duration=duration,
                job_data=job
            )

            # Append the created action to the list of possible actions
            job_target_data.append(script_action)

            # Reduce the remaining energy by the number of actions taken for this job
            actions -= min(possible_actions, actions)

            # If the remaining energy becomes zero, stop adding more actions
            if actions == 0:
                return job_target_data

        return job_target_data

    def target_simulate(self, work_data_list: list[WorkJobData], exp_target: int) -> ExpScriptActionList:
        """
        Simulates targeting a specific experience goal by selecting appropriate actions.

        Args:
            work_data_list (list[WorkJobData]): List of available work job data.
            exp_target (int): Target experience value.

        Returns:
            ExpScriptActionList: List of selected actions.
        """
        # Copy the list of work job data and reverse it
        work_list = work_data_list.copy()
        work_list.reverse()

        # Iterate over the reversed list of work job data
        while len(work_list) != 0:
            # Get the possible action list for the current set of work job data
            action_list = self.get_possible_action_list(
                work_job_data=work_list,
                duration=self.duration
            )

            # If the total experience gained from the selected actions meets or exceeds the target, return the action list
            if action_list.calc_exp() >= exp_target:
                return action_list

            # Move to the next set of work job data by removing the first element from the list
            work_list = work_list[1::]

        # If no combination of actions meets the target, return the list of actions based on the last set of work job data
        return self.get_possible_action_list(work_job_data=work_list, duration=self.duration) #self.work_data_list


class ExpScript:
    """
    Orchestrates the process of selecting and executing work actions.
    
    Attributes:
        game_classes (Game_classes): An instance of the Game_classes containing game-related data.
        script_job_manager (ExpScriptJobDataManager): An instance of ExpScriptJobDataManager for managing job data.
        script_selector (ExpScriptJobSelector): An instance of ExpScriptJobSelector for selecting work actions.
        map (Map): An instance of Map representing the game map.
    """

    def __init__(self,
                 game_classes: Game_classes,
                 script_job_manager: ExpScriptJobDataManager,
                 script_selector: ExpScriptJobSelector,
                 map: Map,
                 level : int
                 ):
        """
        Initializes an ExpScript object.

        Args:
            game_classes (Game_classes): An instance of the Game_classes containing game-related data.
            script_job_manager (ExpScriptJobDataManager): An instance of ExpScriptJobDataManager for managing job data.
            script_selector (ExpScriptJobSelector): An instance of ExpScriptJobSelector for selecting work actions.
            map (Map): An instance of Map representing the game map.
            level (int) : Target level
        """
        self.game_classes = game_classes
        self.script_job_manager = script_job_manager
        self.script_selector = script_selector
        self.map = map
        self.level = level

    def _get_job_data_list(self) -> list[WorkJobData]:
        """
        Retrieves a list of work job data filtered based on sorting and validation rules.

        Returns:
            list[WorkJobData]: A list of WorkJobData objects representing the filtered work job data.
        """
        return self.script_job_manager.get_filtered_job_data()

    def target_exp(self) -> int:
        """
        Retrieves the target experience required by the player.

        Returns:
            int: The target experience required by the player.
        """
        return self.game_classes.player_data.required_exp

    def get_script_actions(self) -> ExpScriptActionList:
        """
        Selects a list of work actions based on the target experience.

        Returns:
            ExpScriptActionList: A list of ExpScriptAction objects representing the selected work actions.
        """
        # Start analyzing the available job offers
        print('Started analysing the job offers')
        # Select work actions based on target experience
        actions = self.script_selector.target_simulate(
            work_data_list=self._get_job_data_list(),
            exp_target=self.target_exp()
        )
        # Filter actions to meet the target experience
        print('Filtering...')
        actions.filter_to_exp_target(exp_target=self.game_classes.player_data.required_exp)

        print(f'Finished. Result is {actions} with a total exp gain of {actions.calc_exp()} . Required {self.game_classes.player_data.required_exp}')
        return actions

    def get_work(self, script_action: ExpScriptAction) -> Work:
        """
        Retrieves the work associated with a given script action.

        Args:
            script_action (ExpScriptAction): An ExpScriptAction object representing the script action.

        Returns:
            Work: A Work object representing the work associated with the script action.
        """
        # Get job ID associated with the script action
        job_id = script_action.job_data.work_id
        # Get the closest job location based on job ID and player data
        location = self.map.get_closest_job(job_id=job_id, player_data=self.game_classes.player_data)
        # Create a Work object based on job ID, location, and duration
        work = Work(
            job_id=script_action.job_data.work_id,
            x=location.job_x,
            y=location.job_y,
            duration=script_action.duration
        )
        return work

    def _work_jobs(self,
                   script_action_list: ExpScriptActionList,
                   callback_function: typing.Callable,
                   *args,
                   **kwargs) -> None:
        """
        Executes work actions and waits for completion.

        Args:
            script_action_list (ExpScriptActionList): A list of ExpScriptAction objects representing work actions.
            callback_function (typing.Callable): A callback function to execute after completing the work.
            *args: Additional positional arguments for the callback function.
            **kwargs: Additional keyword arguments for the callback function.
        """
        # Iterate through the list of script actions
        for action in script_action_list:
            # Execute each work action
            Script_work_task(
                work_manager=self.game_classes.work_manager,
                work_data=self.get_work(script_action=action),
                number_of_actions=action.action_number,
                game_classes=self.game_classes
            ).execute(callback_function=callback_function,
                      *args,
                      **kwargs
                      )

        # Wait until all work actions are completed
        self.game_classes.work_manager.wait_until_free_queue(callback_function,
                                                             *args,
                                                             **kwargs
                                                             )

    @handle_exceptions
    def cycle_exp(self, callback_function: typing.Callable, *args, **kwargs):
        """
        Executes a cycle of work actions to gain experience.

        Args:
            callback_function (typing.Callable): A callback function to execute after completing the work cycle.
            *args: Additional positional arguments for the callback function.
            **kwargs: Additional keyword arguments for the callback function.
        """
        # Check if the player has energy to perform work
        if self.game_classes.player_data.energy == 0 or self.level <= self.game_classes.player_data.level :
            return

        # Get the list of script actions
        actions = self.get_script_actions()
        print(f'{len(actions)}')
        # Iterate until there are no more actions or the target experience is reached
        while len(actions) != 0 and self.game_classes.player_data.level < self.level:

            level = self.game_classes.player_data.level

            print(f'Started work, current level is {level}')
            # Execute work actions
            self._work_jobs(script_action_list=actions,
                            callback_function=callback_function,
                            *args,
                            **kwargs
                            )

            # Update player data after completing work
            self.game_classes.player_data.update_character_variables(handler=self.game_classes.handler)
            print(f'finished working, the level is now: {self.game_classes.player_data.level}')

            # Get new script actions for the next cycle
            actions = self.get_script_actions()
