import typing

from the_west_inner.game_classes import Game_classes
from the_west_inner.player_data import Player_data
from the_west_inner.equipment import Equipment_manager
from the_west_inner.work_manager import Work_manager
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

    def __str__(self) -> str:
        return f'ExpScriptAction(action_number={self.action_number},duration={self.duration},job_data={self.job_data})'
    
    def __repr__(self) -> str:
        return self.__str__()
    
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
    
    def __iter__(self) -> typing.Iterator[ExpScriptAction]:
        
        return iter(self.exp_action_list)
    
    def pop_last_action_number(self):
        if self.exp_action_list:
            last_action = self.exp_action_list[-1]
            last_action.action_number -= 1
            if last_action.action_number == 0:
                self.exp_action_list.pop()
    
    def filter_to_exp_target(self, exp_target : int) -> None:
        if self.calc_exp() < exp_target or len(self.exp_action_list) == 0:
            return 
        practice_action_list = self.copy()
        
        practice_action_list.pop_last_action_number()
        
        while exp_target < practice_action_list.calc_exp() and len(self.exp_action_list) != 0:
            
            self.pop_last_action_number()
            
            practice_action_list.pop_last_action_number()

    def __len__(self) -> int:
        return sum([x.action_number for x in self.exp_action_list])
    
    def __str__(self) -> str:
        
        return f'{self.exp_action_list}'
            
    
class ExpScriptJobSelector():
    def __init__(self,
                 duration : int,
                 player_data : Player_data
                 ):
        
        
        self.duration = duration
        self.player_data = player_data
    def get_possible_action_list(self , work_job_data : list[WorkJobData] , duration : int) -> ExpScriptActionList:
        
        job_target_data = ExpScriptActionList()
        actions = self.player_data.energy
        
        for job in work_job_data:
            
            possible_actions = job.motivation * 100 - 75
            
            if possible_actions <= 0 :
                continue
            
            
            script_action = ExpScriptAction(
                action_number = int(min(possible_actions , actions)),
                duration = duration,
                job_data = job
            )
            
            job_target_data.append(script_action)
            
            actions -= min(possible_actions , actions)
            
            if actions == 0:
                
                return job_target_data
        return job_target_data
    
    def target_simulate(self,work_data_list : list[WorkJobData] , exp_target : int) -> ExpScriptActionList:
        
        work_list = work_data_list.copy()
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
                 game_classes : Game_classes ,
                 script_job_manager : ExpScriptJobDataManager,
                 script_selector : ExpScriptJobSelector,
                 map : Map
                 ):
        self.game_classes = game_classes
        self.script_job_manager = script_job_manager
        self.script_selector = script_selector
        self.map = map
    
    def _get_job_data_list(self) -> list[WorkJobData]:
        
        return self.script_job_manager.get_filtered_job_data()
    
    def target_exp(self) -> int:
        return self.game_classes.player_data.required_exp
    
    def get_script_actions(self) -> ExpScriptActionList:
        print('Started analysing the job offers')
        actions = self.script_selector.target_simulate(
            work_data_list = self._get_job_data_list(),
            exp_target = self.target_exp()
        )
        print('Filtering...')
        actions.filter_to_exp_target(exp_target = self.game_classes.player_data.required_exp)
        
        print(f'Finished. Result is {actions} with a total exp gain of {actions.calc_exp()} . Required {self.game_classes.player_data.required_exp}')
        return actions
    
    def get_work(self, script_action : ExpScriptAction) -> Work:
        
        job_id = script_action.job_data.work_id
        
        location = self.map.get_closest_job(job_id = job_id,player_data= self.game_classes.player_data)
        
        work = Work(
            job_id = script_action.job_data.work_id,
            x = location.job_x,
            y = location.job_y,
            duration = script_action.duration
        )
        
        return work
        
    
    def _work_jobs(self , 
                   script_action_list : ExpScriptActionList ,
                   callback_function : typing.Callable ,
                   *args ,
                   **kwargs) -> None:
        
        
        for action in script_action_list:
            
            Script_work_task(
                work_manager = self.game_classes.work_manager,
                work_data = self.get_work(script_action = action),
                number_of_actions = action.action_number,
                game_classes = self.game_classes
            ).execute(callback_function = callback_function,
                    *args,
                    **kwargs
                      )

        self.game_classes.work_manager.wait_until_free_queue()
        
    def cycle_exp(self , callback_function : typing.Callable , *args , **kwargs) :
        
        if self.game_classes.player_data.energy == 0:
            
            return
        
        actions = self.get_script_actions()
        print(f'{len(actions)}')
        while len(actions) != 0 :
            
            level = self.game_classes.player_data.level
            
            print(f'Started work , current level is {level}')
            self._work_jobs(script_action_list = actions,
                            callback_function = callback_function,
                            *args,
                            **kwargs
                            )
            
            self.game_classes.player_data.update_character_variables(handler=self.game_classes.handler)
            print(f'finished working the level is now : {self.game_classes.player_data.level}')
            
            actions = self.get_script_actions()