import math

from the_west_inner.requests_handler import requests_handler
from the_west_inner.task_queue import TaskQueue
from the_west_inner.premium import Premium
from the_west_inner.player_data import Player_data
from the_west_inner.misc_scripts import wait_until_date,wait_until_date_callback

class Work_manager():
    """A class for managing work tasks in a task queue.

    Attributes:
        handler (requests_handler): An object for handling HTTP requests.
        task_queue (TaskQueue): A task queue object.
        premium (Premium): A premium object.
        player_data (Player_data): A player data object.
    """

    def __init__(self, handler: requests_handler, task_queue: TaskQueue, premium: Premium, player_data: Player_data):
        self.handler = handler
        self.task_queue = task_queue
        self.premium = premium
        self.player_data = player_data

    def update_task_queue(self, data):
        """Update the task queue.

        Args:
            data (list): A list of task data.
        """
        try :
            if type(data) != list:
                data = data.values()
            self.task_queue.update(list([x["task"] for x in data if 'task' in x]))
        except Exception as e :
            print(data)
            raise e
    def update_player_data(self, data):
        """Update the player data.

        Args:
            data (int): The amount of energy consumed.
        """
        self.player_data.update_energy(data)

    def work(self, work_object, number_of_tasks=1):
        """Add a work task to the task queue.

        Args:
            work_object (Work_object): A work object to be added to the queue.
            number_of_tasks (int, optional): The number of tasks to be added. Defaults to 1.

        Returns:
            dict: A dictionary containing the server's response.
        """
        # Get the current position in the task queue.
        position_in_queue = len(self.task_queue)

        # Get the maximum number of tasks that can be added to the queue.
        allowed_tasks = {True: 9, False: 4}[self.premium.automation]

        # If the number of tasks to be added exceeds the maximum allowed,
        # reduce the number of tasks to the maximum allowed.
        if position_in_queue + number_of_tasks > allowed_tasks:
            number_of_tasks = allowed_tasks - position_in_queue

        # Create a dictionary to store the task data.
        job_dict = {}

        # Dictionary mapping work durations to the amount of energy consumed.
        energy_dict = {15: 1, 600: 5, 3600: 12}

        # Calculate the total amount of energy consumed by the tasks.
        consumed_energy = number_of_tasks * energy_dict[work_object.duration]

        # If the player doesn't have enough energy, reduce the number of tasks
        # to the maximum number the player can do with their current energy.
        if consumed_energy > self.player_data.energy:
            consumed_energy = self.player_data.energy // energy_dict[work_object.duration]

        # Add the tasks to the dictionary.
        for i in range(number_of_tasks):
            # Add the task data to the dictionary.
            job_dict[f"tasks[{position_in_queue+ i}][jobId]"] = f"{work_object.job_id}",
            job_dict[f"tasks[{position_in_queue+ i}][x]"] = f"{work_object.x}",
            job_dict[f"tasks[{position_in_queue+ i}][y]"] = f"{work_object.y}",
            job_dict[f"tasks[{position_in_queue+ i}][duration]"] = f"{work_object.duration}",
            job_dict[f"tasks[{position_in_queue+ i}][taskType]"] = "job"

        # Send the tasks to the server and get the response.
        response = self.handler.post("task", "add", payload=job_dict, use_h=True)

        # Update the task queue and player data with the server's response.
        self.update_task_queue(response["tasks"])
        self.update_player_data(math.floor(response["energy"]))

        # Return the server's response.
        return response

    def move_to_town(self, town_id: str):
        """Add a task to move to a given town.

        Args:
            town_id (str): The ID of the town to move to.

        Returns:
            dict: A dictionary containing the server's response.
        """
        # Get the current position in the task queue.
        position_in_queue = len(self.task_queue)

        # Get the maximum number of tasks that can be added to the queue.
        allowed_tasks = {True: 9, False: 4}[self.premium.automation]

        # If the task queue is full, wait until the earliest task finishes before adding the new task.
        if position_in_queue + 1 > allowed_tasks:
            wait_until_date(wait_time=self.task_queue.get_tasks_expiration(), handler=self.handler)
            position_in_queue = 0

        # Create a dictionary to store the task data.
        payload_deplasare = {
            f"tasks['{position_in_queue}'][unitId]": f"{town_id}",
            f"tasks['{position_in_queue}'][type]": "town",
            f"tasks['{position_in_queue}'][taskType]": "walk"
        }

        # Send the task to the server and get the response.
        response = self.handler.post("task", "add", payload=payload_deplasare, use_h=True)

        # Return the server's response.
        return response
    
    def move_to_quest_employer(self, quest_employer_key: str,x:int,y:int):
        """Add a task to move to a given quest employer.

        Args:
            quest_employer_key (str): The ID of the quest employer to move to.
            x , y (int): The position of the quest employer on the map

        Returns:
            dict: A dictionary containing the server's response.
        """
        # Get the current position in the task queue.
        position_in_queue = len(self.task_queue)

        # Get the maximum number of tasks that can be added to the queue.
        allowed_tasks = {True: 9, False: 4}[self.premium.automation]

        # If the task queue is full, wait until the earliest task finishes before adding the new task.
        if position_in_queue + 1 > allowed_tasks:
            wait_until_date(wait_time=self.task_queue.get_tasks_expiration(), handler=self.handler)
            position_in_queue = 0

        # Create a dictionary to store the task data.
        payload_walk = {
            f"tasks['{position_in_queue}'][unitId]": quest_employer_key,
            f"tasks['{position_in_queue}'][type]": "questgiver",
            f"tasks['{position_in_queue}'][x]": x,
            f"tasks['{position_in_queue}'][y]": y,
            f"tasks['{position_in_queue}'][taskType]": "walk"
        }

        # Send the task to the server and get the response.
        response = self.handler.post("task", "add", payload=payload_walk, use_h=True)

        # Return the server's response.
        
        return response
    
    def allowed_tasks(self):
        """Get the number of tasks that can be added to the task queue.

        Returns:
            int: The number of tasks that can be added to the queue.
        """
        # Get the current position in the task queue.
        position_in_queue = len(self.task_queue)

        # Get the maximum number of tasks that can be added to the queue.
        allowed_tasks = {True: 9, False: 4}[self.premium.automation]

        # Return the number of tasks that can be added to the queue.
        return allowed_tasks - position_in_queue

    def max_allowed_tasks(self):
        """Get the maximum number of tasks that can be added to the task queue.

        Returns:
            int: The maximum number of tasks that can be added to the queue.
        """
        # Return the maximum number of tasks that can be added to the queue.
        return {True: 9, False: 4}[self.premium.automation]

    def free_queue(self):
        """Check if the task queue is empty.

        Returns:
            bool: True if the task queue is empty, False otherwise.
        """
        # Return True if the task queue is empty, False otherwise.
        return self.allowed_tasks() == self.max_allowed_tasks()
    #def wait_until_free_queue(self):
    #    """Waits until the queue is empty."""
    #    wait_until_date(wait_time=self.task_queue.get_tasks_expiration(), handler=self.handler)
        
    def wait_until_free_queue(self , callback , *args , **kwargs):
        """Waits until the queue is empty but uses the asynchronous method to callback other functions on wait."""

        wait_until_date_callback(
            wait_time = self.task_queue.get_tasks_expiration(),
            handler= self.handler ,
            callback_function = callback , 
            *args ,
            **kwargs 
        )
    
    def sleep_task(self,room_type:str,town_id:int):
        """Add a task to sleep in a given room of a town.

        Args:
            town_id (str): The ID of the town to move to.

        Returns:
            dict: A dictionary containing the server's response.
        """
        # Get the current position in the task queue.
        position_in_queue = len(self.task_queue)

        # Get the maximum number of tasks that can be added to the queue.
        allowed_tasks = {True: 9, False: 4}[self.premium.automation]

        # If the task queue is full, wait until the earliest task finishes before adding the new task.
        if position_in_queue + 1 > allowed_tasks:
            wait_until_date(wait_time=self.task_queue.get_tasks_expiration(), handler=self.handler)
            position_in_queue = 0

        # Create a dictionary to store the task data.
        sleep_payload = {
            f"tasks['{position_in_queue}'][town_id]": f"{town_id}",
            f"tasks['{position_in_queue}'][type]": room_type,
            f"tasks['{position_in_queue}'][taskType]": "sleep"
        }

        # Send the task to the server and get the response.
        response = self.handler.post("task", "add", payload=sleep_payload, use_h=True)

        # Return the server's response.
        return response
    def pray_task(self,town_id:int):
        """Add a task to pray in a town.

        Args:
            town_id (str): The ID of the town to move to.

        Returns:
            dict: A dictionary containing the server's response.
        """
        # Get the current position in the task queue.
        position_in_queue = len(self.task_queue)

        # Get the maximum number of tasks that can be added to the queue.
        allowed_tasks = {True: 9, False: 4}[self.premium.automation]

        # If the task queue is full, wait until the earliest task finishes before adding the new task.
        if position_in_queue + 1 > allowed_tasks:
            wait_until_date(wait_time=self.task_queue.get_tasks_expiration(), handler=self.handler)
            position_in_queue = 0

        # Create a dictionary to store the task data.
        sleep_payload = {
            f"tasks['{position_in_queue}'][town_id]": f"{town_id}",
            f"tasks['{position_in_queue}'][taskType]": "pray"
        }

        # Send the task to the server and get the response.
        response = self.handler.post("task", "add", payload=sleep_payload, use_h=True)

        # Return the server's response.
        return response
    def cancel_all_tasks(self) :
        
        self.task_queue.tasks.cancel()