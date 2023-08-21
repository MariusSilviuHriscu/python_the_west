import concurrent.futures
import time
import functools

class Script_clona_process():
    """
    Represents a scheduled function call process.

    Attributes:
        scheduled_function_call (functools.partial): The function to be called.
        status (str): The status of the process ("pending" or "completed").
    """

    def __init__(self, scheduled_function_call: functools.partial):
        self.function = scheduled_function_call
        self.status = "pending"
    
    def execute(self):
        """
        Execute the scheduled function and update the status.
        """
        self.status = "pending"
        self.function()
        self.status = "completed"
        print("Finished scheduled task!")

class Script_schedule():
    """
    Manages the scheduling and execution of Script_clona_process instances.
    """

    def __init__(self) -> None:
        self.processes = []
    
    def add_process(self, process: Script_clona_process):
        """
        Add a Script_clona_process to the schedule.

        Args:
            process (Script_clona_process): The process to be added.
        """
        self.processes.append(process)
    
    def start(self):
        """
        Start the execution of scheduled processes in a separate process pool.
        """
        with concurrent.futures.ProcessPoolExecutor() as executor:
            while True:
                # Start each process in a separate worker process
                # Check the status of each process every hour
                futures = [executor.submit(process.execute) for process in self.processes if process.status == "pending"]
                time.sleep(3600)  # Wait for an hour

                