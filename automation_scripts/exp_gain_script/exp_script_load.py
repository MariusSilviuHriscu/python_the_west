from the_west_inner.game_classes import Game_classes

from the_west_inner.work_job_data import WorkDataLoader,WorkJobDataManager,ExpDamageRule,DamageValidationRule,FrequencyDamageValidationRule
from the_west_inner.map import Map,MapLoader
from automation_scripts.exp_gain_script.exp_script import ExpScriptJobSelector,ExpScript,ExpScriptJobDataManager
from automation_scripts.exp_gain_script.exp_script import WorkSortRule,WorkValidationRule

class ExpScriptDataManagerLoader():
    
    def __init__(self ,
                 game_classes : Game_classes,
                 work_sort_rule_list : list[WorkSortRule],
                 work_validation_rule_list : list[WorkValidationRule]
                 ):
        self.game_classes = game_classes
        self.work_sort_rule_list = work_sort_rule_list
        self.work_validation_rule_list = work_validation_rule_list
            
    
    def _load_work_data_loader(self,map : Map ) -> WorkDataLoader:
        
        return WorkDataLoader(handler = self.game_classes.handler,
                              player_data = self.game_classes.player_data,
                              map = map
                              )
    
    def load(self , map : Map) -> ExpScriptJobDataManager:
        
        return ExpScriptJobDataManager(
            work_data_loader= self._load_work_data_loader(map= map),
            work_sort_rule_list = self.work_sort_rule_list ,
            work_validation_rule_list=self.work_validation_rule_list
            
        )


class ExpScriptLoader():
    
    def __init__(self ,
                 game_classes : Game_classes,
                 job_script_manager_loader : ExpScriptDataManagerLoader,
                 script_selector : ExpScriptJobSelector,
                 map : Map
                 ) :
        self.game_classes = game_classes
        self.job_script_manager_loader = job_script_manager_loader
        self.script_selector = script_selector
        self.map = map
    def load(self) -> ExpScript:
        return ExpScript(game_classes = self.game_classes,
                         script_job_manager = self.job_script_manager_loader.load(map = self.map),
                         script_selector = self.script_selector,
                         map = self.map
                         )


def load_exp_script(game_classes : Game_classes):
    
    map = MapLoader(
            handler = game_classes.handler,
            player_data = game_classes.player_data,
            work_list = game_classes.work_list
        ).build()
    
    exp_rule = ExpDamageRule(
    time_value= 15
    )
    damage_validation_rule = DamageValidationRule(
        handler=game_classes.handler,
        player_data=game_classes.player_data,
        map = map,
        max_allowed_damage_percent = 0.25
    )
    frequency_validation_rule = FrequencyDamageValidationRule(
        handler=game_classes.handler,
        player_data=game_classes.player_data,
        map = map,
        max_allowed_damage_frequency = 0.15
    )
    
    
    job_script_manager_loader = ExpScriptDataManagerLoader(
        game_classes = game_classes,
        work_sort_rule_list = [exp_rule],
        work_validation_rule_list = [damage_validation_rule,frequency_validation_rule]
        
    )
    selector = ExpScriptJobSelector(
    duration= 15,
    player_data = game_classes.player_data
    )
    
    exp_script_loader = ExpScriptLoader(
        game_classes = game_classes,
        job_script_manager_loader = job_script_manager_loader,
        script_selector= selector,
        map = map
    )
    
    return exp_script_loader.load()