
from the_west_inner.work_job_data import WorkJobData


class MoneyScriptAction:
    """
    Represents an action in the MoneyScript, including the number of actions, duration, and associated work job data.

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
    
    
    def calc_worktime(self) -> int:
        """
        Calculates the total work time for the action.
        
        Returns:
            int: Total work time.
        """
        return self.duration * self.action_number

    def __str__(self) -> str:
        """
        Returns a string representation of the MoneyScriptAction object.
        
        Returns:
            str: String representation.
        """
        return f'MoneyScriptAction(action_number={self.action_number}, duration={self.duration}, job_data={self.job_data})'
    
    def __repr__(self) -> str:
        """
        Returns a string representation of the MoneyScriptAction object.
        
        Returns:
            str: String representation.
        """
        return self.__str__()