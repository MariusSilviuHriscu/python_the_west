import typing
from the_west_inner.map import Map, Map_job_location
from the_west_inner.player_data import Player_data
from the_west_inner.requests_handler import requests_handler
from the_west_inner.work_job_data import WorkJobData, WorkJobDataManager, WorkSortRule, WorkValidationRule
from the_west_inner.movement_manager import MovementManager


class WorkCycleJobSimul:
    
    def __init__(self,
                 map_job_location : Map_job_location,
                 job_data :WorkJobData):
        self.map_job_location = map_job_location
        self.job_data = job_data
    

class WorkCycleSimul:
    
    def __init__(self , work_data_list : list[WorkCycleJobSimul]):
        
        self.work_data_list = work_data_list
    
    
    def is_valid_cycle(self ) -> bool :
        
        work_id_list = [x.job_data.work_id for x in self.work_data_list]
        return len(set(work_id_list)) == len(work_id_list)


class Work_cycle_simul_data:
    
    def __init__(self ,
                 complete_job_locations : typing.Dict[typing.Tuple[int,int,int],Map_job_location] ,
                 handler : requests_handler,
                 player_data : Player_data ,
                 movement_manager : MovementManager,
                 job_data_manager : WorkJobDataManager
                 ):
        self.handler = handler
        self.complete_job_location = complete_job_locations
        self.player_data = player_data
        self.movement_manager = movement_manager
        self.job_data_manager = job_data_manager
    
    def _get_list_of_work(self,
                        work_sort_rules : list[WorkSortRule],
                        filter_rules : list[WorkValidationRule]| None = None,
                        max_number:typing.Optional[int] = None) -> typing.Generator[WorkCycleJobSimul,None,None]:
        
        universal_job_data = self.job_data_manager.sort_by_work_sort_rule(
            work_sort_rules= work_sort_rules,
            filter_rules = filter_rules,
            max_number = max_number
        )
        
        
        universal_job_data_dict = {x.work_id : x for x in universal_job_data}        
        
        for job_location_data in self.complete_job_location.values():
            
            if job_location_data.job_id in universal_job_data_dict:
                
                
                job_data = universal_job_data_dict.get(job_location_data.job_id)
                
                
                yield WorkCycleJobSimul(
                    map_job_location = job_location_data,
                    job_data = job_data
                )
        
    def get_list_of_work(self,
                        work_sort_rules : list[WorkSortRule],
                        filter_rules : list[WorkValidationRule]| None = None,
                        max_number:typing.Optional[int] = None) -> list[WorkCycleJobSimul]:
        
        return [x for x in self._get_list_of_work(work_sort_rules= work_sort_rules,
                                                  filter_rules= filter_rules,
                                                  max_number= max_number
                                                  )]