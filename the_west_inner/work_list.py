import typing
from dataclasses import dataclass

from requests_handler import requests_handler
from player_data import Player_data


@dataclass
class WorkData:
    cost : int
    money : int
    xp : int
    luck : int
    duration : int
    product_id_list : list[int]
    
    
@dataclass
class JobDataDamage:
    damage_probability : int
    damage_max_damage : int
    
    def average_damage(self , max_hp : int) ->int:
        return self.damage_max_damage * self.damage_probability * max_hp
class WorkJobData:
    def __init__(self,
                 work_id : int ,
                 skill_points_required : int,
                 work_points : int,
                 motivation : int,
                 item_drop_interval : tuple[int,int] ,
                 stage : int ,
                 malus : int ,
                 timed_work_data : dict[typing.Literal[15,600,3600] : WorkData]
                ):

        self.work_id = work_id
        self.skill_points_required = skill_points_required
        self.work_points = work_points
        self.motivation = motivation
        self.item_drop_interval = item_drop_interval
        self.stage = stage
        self.malus = malus
        self.timed_work_data = timed_work_data

        self._job_data_damage = None
        self._job_data = None
        
    def _load_job_data(self , handler : requests_handler , x : int, y : int) -> None :
        
        payload = {
            'jobId' : self.work_id,
            'x' : x,
            'y' : y
        }
        
        response = handler.post(window='job',action='job',action_name='mode',payload=payload)
        
        
        self._job_data = response
            
        return response
    
    @property
    def job_data(self) -> dict:
        
        return self._job_data
    
    def job_data_damage(self) -> JobDataDamage:
        return self._job_data_damage
    
    def load_joab_damage(self, handler : requests_handler , x : int , y : int) -> JobDataDamage:
        
        if self.job_data is None:
            
            self._load_job_data(
                handler= handler,
                x = x ,
                y = y)
        
        job_damage = JobDataDamage(
            damage_probability = self.job_data.get('danger'),
            damage_max_damage= self.job_data.get('maxdmg')
        )
        
        self._job_data_damage = job_damage
        
        return job_damage
        
        
class WorkJobDataManager:
    
    def __init__(self , 
                 player_data : Player_data ,
                 work_job_data_list : list[WorkJobData] ,
                 ) :
        self.player_data = player_data
        self.work_job_data_list = work_job_data_list
        self.work_dict = {x.work_id : x for x in work_job_data_list}
    
    
class Work_list():
    """A class for managing a list of work items.

    Attributes:
        work_dict (dict): A dictionary of work items, indexed by their ID.
    """

    def __init__(self, work_list):
        """Initialize the work list.

        Args:
            work_list (list): A list of work items.
        """
        self.work_dict = {work["id"]:work for work in work_list}

    def get_group_id(self, work_id):
        """Get the group ID of a work item.

        Args:
            work_id (int): The ID of the work item.

        Returns:
            int: The group ID of the work item.
        """
        return self.work_dict[work_id]["groupid"]

    def work_products(self):
        """Get a dictionary of possible products that can be produced by the work items.

        Returns:
            dict: A dictionary mapping each product to its associated work item ID and level.
        """
        possible_yields = {}
        for yields in self.work_dict.values():
            # Skip items that don't have yields.
            if type(yields) == list:
                continue
            for product in yields["yields"]:
                # Add the product to the dictionary if it hasn't been seen before.
                if product not in possible_yields:
                    possible_yields[product] = None

        for work in self.work_dict.values():
            # Skip items that don't have yields.
            if type(work["yields"]) == list:
                continue
            for product in work["yields"].keys():
                # Associate the product with its work item ID and level.
                possible_yields[product] = {"id": work["id"], "level": work["level"]}

        return possible_yields

    def motivation(self, handler: requests_handler):
        """Get the motivation levels of the work items.

        Args:
            handler (requests_handler): An object for handling HTTP requests.

        Returns:
            dict: A dictionary mapping each work item's ID to its motivation level.
        """
        # Send an HTTP request to get the motivation levels of the work items.
        motivation_dict = handler.post(window="work", action="index", action_name="mode")["jobs"]

        # Return a dictionary mapping each work item's ID to its motivation level.
        return {x: int(float(motivation_dict[x]['motivation']) * 100) for x in motivation_dict}
    def _load_work_data(self , work_data : dict) -> WorkData:
        return WorkData(
            cost = work_data.get('cost'),
            money = work_data.get('money'),
            xp = work_data.get('xp'),
            luck = work_data.get('luck'),
            duration = work_data.get('duration'),
            product_id_list = [x.get('itemid',None) for x in work_data.get('items') if x.get('itemid',None) is not None]
        )
    def _load_work_info(self , job_id:int|str , job_dict: dict) -> WorkJobData:
        work_time_info = job_dict.get('durations')
        return WorkJobData(
            work_id = int(job_id),
            skill_points_required = job_dict.get('jobSkillPoints'),
            work_points = job_dict.get('workpoints'),
            motivation = job_dict.get('motivation'),
            item_drop_interval = (job_dict.get('minMaxItemVal')[0] , job_dict.get('minMaxItemVal')[1]),
            stage = job_dict.get('stage').get('stage'),
            malus= job_dict.get('stage').get('malus'),
            timed_work_data = {x.get('duration') : self._load_work_data(work_data = x) 
                                                    for x in work_time_info}
        )
        
    def get_work_info(self,handler:requests_handler) -> list[WorkJobData]:
        
        response = handler.post(window="work", action="index", action_name="mode")['jobs']
        
        return [self._load_work_info(job_id = job_id,
                                     job_dict = job_dict
                                     ) for job_id,job_dict in response.items()]