"""
This module handles task management in a game being played using the requests_handler class. 
It contains four classes: Task, Task_list, TaskQueue, and Task_type.

Classes:
    The Task class: Represents a task in the game and has attributes for the expiration date, start date, type, task data, queue ID, and queue position of the task. It also has a method to cancel the task.

    The Task_list : This class is for managing a list of tasks and has an attribute for a list of task objects. It has a method to cancel all tasks in the list.

    The TaskQueue:  This class is for managing a queue of tasks and has attributes for the requests_handler instance, player data, and a list of task objects. It has methods to update the task queue, get the number of tasks in the queue, and cancel all tasks in the queue.

    The Task_type : This class is a simple enum-like class for storing constants representing the different types of tasks that can be added to the task queue.
"""

from requests_handler import requests_handler
import datetime
import time
from player_data import Player_data

class Task():
    """
    Represents a task in a game being played using the requests_handler class.
    Attributes:
        handler (requests_handler): The `requests_handler` instance used to make requests to the game server.
        expiration_date (datetime.datetime): The date and time at which the task will expire.
        start_date (datetime.datetime): The date and time at which the task was started.
        type (str): The type of task.
        task_data (dict): The task data, containing information about the task.
        queue_id (str): The ID of the task in the task queue.
        queue_position (int): The position of the task in the task queue.
    """
    def __init__(self, handler:requests_handler, raw_task_data, queue_position):
        """
        Initializes a new `Task` instance from the given raw task data and queue position.
        
        Args:
            handler (requests_handler): The `requests_handler` instance used to make requests to the game server.
            raw_task_data (dict): The raw task data, as returned by the game server.
            queue_position (int): The position of the task in the task queue.
        """
        self.handler = handler
        self.expiration_date = datetime.datetime.strptime(time.ctime(raw_task_data["date_done"]),"%c")
        self.start_date = raw_task_data["date_start"]
        # Determine the type of the task by checking for the existence of either the
        # "type" or "name" keys in the raw task data.
        self.type = raw_task_data.get("type") or raw_task_data.get("name")
        if 'data' in raw_task_data:
            self.task_data = raw_task_data['data']
        elif 'data_obj' in raw_task_data:
            self.task_data = raw_task_data["data_obj"]
        self.queue_id = raw_task_data["queue_id"]
        self.queue_position = queue_position
    
    def cancel(self):
        """
        Makes a request to cancel the task.
        
        Returns:
            dict: The JSON response from the server.
        """
        # Construct the payload for the request by adding the task's queue ID and type
        # to the payload using the task's queue position as the index.
        payload = {
            f"tasks[{self.queue_position}][queueId]": f"{self.queue_id}",
            f"tasks[{self.queue_position}][type]": f"{self.type}"
        }
        # Make a POST request to the "task" window with the "cancel" action,
        # including the constructed payload and the `h` query parameter.
        return self.handler.post("task", "cancel", payload=payload, use_h=True)

class Task_list():
    """A class for managing a list of tasks.

    Attributes:
        task_list (list): A list of task objects.
    """

    def __init__(self, task_list):
        """Initialize the task list.

        Args:
            task_list (list): A list of task objects.
        """
        self.task_list = task_list

    def cancel(self):
        """Cancel all tasks in the list.

        Returns:
            bool: True if all tasks were successfully cancelled, False otherwise.
        """
        for task in self.task_list:
            returnable = task.cancel()
        return returnable

class TaskQueue():
    """A class for managing a queue of tasks.

    Attributes:
        handler (requests_handler): An object for handling HTTP requests.
        player_data (Player_data): An object containing player data.
        task_queue (list): A list of task objects.
    """

    def __init__(self, handler: requests_handler, player_data: Player_data):
        """Initialize the task queue.

        Args:
            handler (requests_handler): An object for handling HTTP requests.
            player_data (Player_data): An object containing player data.
        """
        self.handler = handler
        self.player_data = player_data
        # Initialize the task queue by sending an HTTP request.
        self.update()

    def initialize(self):
        """Initialize the task queue by sending an HTTP request.

        Returns:
            list: A list of tasks.
        """
        data = self.handler.post("task","","action",None)
        
        if 'queue' not in data:
            raise Exception(f'Could not find the queue field in the response : {data}')
        
        return data["queue"]

    def update(self, data= None):
        """Update the task queue with the current list of tasks.

        Args:
            data (list): A list of tasks. If not provided, the task queue
                         is initialized by sending an HTTP request.

        Returns:
            None
        """
        if data is None:
            # Initialize the task queue by sending an HTTP request if no data is provided.
            data = self.initialize()
        self.task_queue = []
        for position, task in enumerate(data):
            # Create a Task object for each task in the queue and append it to the task_queue attribute.
            self.task_queue.append(Task(self.handler, task, position))
    def sleep_task_in_queue(self):
        """Check whether there is a "sleep" task in the queue.

        Returns:
            bool: True if there is a "sleep" task in the queue, False otherwise.
        """
        # Update the task queue to get the current list of tasks.
        self.update()
        for task in self.task_queue:
            # Check if the type of the task is "sleep".
            if task.type == "sleep":
                return True
        # Return False if no "sleep" task was found.
        return False

    def get_tasks_number(self):
        """Get the number of tasks in the queue.

        Returns:
            int: The number of tasks in the queue.
        """
        # Update the task queue to get the current list of tasks.
        self.update()
        # Return the length of the task_queue attribute.
        return len(self.task_queue)

    def get_tasks_expiration(self):
        """Get the expiration date of the last task in the queue.

        Returns:
            datetime: The expiration date of the last task in the queue.
                      If the queue is empty, returns -1.
        """
        # Update the task queue to get the current list of tasks.
        self.update()
        # Return the expiration_date attribute of the last task in the queue,
        # or -1 if the queue is empty.
        return self.task_queue[-1].expiration_date  if len(self.task_queue) != 0  else -1

    def get_task_expiration_in_seconds(self):
        """Get the expiration time of the last task in the queue in seconds.

        Returns:
            int: The expiration time of the last task in the queue in seconds.
                 If the queue is empty, returns 0.
        """
        # Get the expiration date of the last task in the queue.
        end_date = self.get_tasks_expiration()
        # Return the expiration time in seconds, or 0 if the queue is empty.
        return end_date.seconds if end_date != -1 else 0

    def return_tasks_by_type(self, task_type) -> Task_list:
        """Get a list of tasks of a given type.

        Args:
            task_type (str): The type of tasks to return.

        Returns:
            Task_list: A list of tasks of the specified type.
        """
        # Update the task queue to get the current list of tasks.
        self.update()
        # Return a Task_list object containing only tasks of the specified type.
        return Task_list(list([task for task in self.task_queue if task.type == task_type]))

    @property
    def tasks(self):
        """Get a list of all tasks in the queue.

        Returns:
            Task_list: A list of all tasks in the queue.
        """
        # Update the task queue to get the current list of tasks.
        self.update()
        # Return a Task_list object containing all tasks in the queue.
        return Task_list(list([task for task in self.task_queue]))

    def cancel_task_by_position(self, position):
        """Cancel a task at a given position in the queue.

        Args:
            position (int): The position of the task to cancel.

        Returns:
            None
        """
        # Cancel the task at the specified position.
        cancelation_data = self.task_queue[position].cancel()
        # Update the task queue with the updated list of tasks.
        self.update(cancelation_data["queue"])

    def __len__(self):
        """Implementation of the built-in len function for the TaskQueue class.

        Returns:
            int: The number of tasks in the queue.
        """
        # Return the number of tasks in the queue.
        return self.get_tasks_number()

