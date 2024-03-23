import typing

from the_west_inner.player_data import Player_data
from the_west_inner.equipment import Equipment_manager,Equipment

from the_west_inner.work_job_data import (WorkDataLoader,
                                          WorkJobDataManager,
                                          WorkSortRule,
                                          WorkValidationRule,
                                          WorkJobData,
                                          WorkData
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


class ExpScriptAction:
    def __init__(self, action_number : int,duration : int , job_data : WorkJobData):
        self.action_number = action_number
        self.duration = duration
        self.job_data = job_data
    
    def calc_exp(self) -> int:
        work_data : WorkData = self.job_data.timed_work_data[self.duration]
        
        return work_data.xp * self.action_number
    
    def calc_worktime(self) -> int:
        
        return self.duration * self.action_number

class ExpScriptActionList:
    def __init__(self , exp_action_list : list[ExpScriptAction]|None = None):
        self.exp_action_list = exp_action_list
        if exp_action_list is None:
            self.exp_action_list = []
    
    def append(self,exp_action : ExpScriptAction):
        self.exp_action_list.append(exp_action)
    
    def calc_exp(self) -> int:
        
        return sum([x.calc_exp() for x in self.exp_action_list])
    
    def calc_worktime(self) -> int:
        
        return sum([x.calc_worktime() for x in self.exp_action_list])
    
    def copy(self) -> typing.Self:
        
        return ExpScriptActionList(
            exp_action_list = [ ExpScriptAction(action_number = x.action_number,
                                                duration = x.duration,
                                                job_data = x.job_data
                                                ) 
                                                for x in self.exp_action_list]
        )
    
    def pop_last_action_number(self):
        if self.exp_action_list:
            last_action = self.exp_action_list[-1]
            last_action.action_number -= 1
            if last_action.action_number == 0:
                self.exp_action_list.pop()
                print(self.exp_action_list[-1])
    
    def filter_to_exp_target(self, exp_target : int) -> None:
        if self.calc_exp() < exp_target or len(self.exp_action_list) == 0:
            return 
        practice_action_list = self.copy()
        
        practice_action_list.pop_last_action_number()
        
        while exp_target < practice_action_list.calc_exp() and len(self.exp_action_list) != 0:
            
            self.pop_last_action_number()
            
            practice_action_list.pop_last_action_number()
        
            
    
class ExpScriptJobSelector():
    def __init__(self,
                 duration : int,
                 work_data_list : list[WorkJobData],
                 player_data : Player_data
                 ):
        
        
        self.duration = duration
        self.work_data_list = work_data_list
        self.player_data = player_data
    def get_possible_action_list(self , work_job_data : list[WorkJobData] , duration : int) -> ExpScriptActionList:
        
        job_target_data = ExpScriptActionList()
        actions = self.player_data.energy
        
        for job in work_job_data:
            
            possible_actions = job.motivation * 100 - 75
            
            if possible_actions <= 0 :
                continue
            
            
            script_action = ExpScriptAction(
                action_number = min(possible_actions , actions),
                duration = duration,
                job_data = job
            )
            
            job_target_data.append(script_action)
            
            actions -= min(possible_actions , actions)
            
            if actions == 0:
                
                return job_target_data
        return job_target_data
    
    def target_simulate(self, exp_target : int) -> ExpScriptActionList:
        
        work_list = self.work_data_list.copy()
        work_list.reverse()
        
        while len(work_list) != 0:
            
            action_list = self.get_possible_action_list(work_job_data = work_list ,
                                                        duration= self.duration
                                                        )
            
            if action_list.calc_exp() >= exp_target:
                return action_list
            
            work_list = work_list[1::]

        return self.get_possible_action_list(work_job_data=self.work_data_list,duration=self.duration)

class ExpScript:
    
    def __init__(self,
                 player_data : Player_data,
                 equipment_manager : Equipment_manager,
                 script_job_manager : ExpScriptJobDataManager):
        self.player_data = player_data
        self.equipment_manager = equipment_manager
        self.script_job_manager = script_job_manager
    
    def _get_job_data_list(self) -> list[WorkJobData]:
        
        return self.script_job_manager.get_filtered_job_data()
    
    def target_exp(self) -> int:
        return self.player_data.required_exp
    