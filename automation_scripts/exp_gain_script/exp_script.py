import typing

from the_west_inner.player_data import Player_data
from the_west_inner.equipment import Equipment_manager,Equipment

from the_west_inner.work_job_data import (WorkDataLoader,
                                          WorkJobDataManager,
                                          WorkSortRule,
                                          WorkValidationRule,
                                          WorkJobData
                                          )


class ExpScriptJobDataManager:
    
    def __init__(self,
                 work_data_loader : WorkDataLoader , 
                 work_sort_rule_list : list[WorkSortRule],
                 work_validation_rule_list : list[WorkValidationRule]
                 ):
        self.work_data_loader = work_data_loader
        self.work_sort_rule_list = work_sort_rule_list
        self.work_validation_rule_list = work_validation_rule_list

    def _get_job_data_manager(self):
        
        return self.work_data_loader.get_work_data_manager()

    @property
    def job_data_manager(self) -> WorkJobDataManager:
        
        return self._get_job_data_manager()
    
    def get_filtered_job_data(self) -> list[WorkJobData]:
        
        return self.job_data_manager.sort_by_work_sort_rule(
            work_sort_rules = self.work_sort_rule_list,
            filter_rules = self.work_validation_rule_list,
        )
    
class ExpScript:
    
    def __init__(self,
                 player_data : Player_data,
                 equipment_manager : Equipment_manager,
                 script_job_manager : ExpScriptJobDataManager):
        self.player_data = player_data
        self.equipment_manager = equipment_manager
        self.script_job_manager = script_job_manager
    
    def _get_job_data_list(self) -> list[WorkJobData]:
        
        