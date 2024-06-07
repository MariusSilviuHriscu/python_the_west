from the_west_inner.game_classes import Game_classes

from the_west_inner.work_job_data import WorkDataLoader,WorkJobDataManager,ExpDamageRule,DamageValidationRule,FrequencyDamageValidationRule
from the_west_inner.map import Map,MapLoader
from automation_scripts.exp_gain_script.exp_script import ExpScriptJobSelector,ExpScript,ExpScriptJobDataManager
from automation_scripts.exp_gain_script.exp_script import WorkSortRule,WorkValidationRule

class ExpScriptDataManagerLoader:
    """
    Loads the necessary data for managing work jobs in the context of experience gain script.
    """

    def __init__(self,
                 game_classes: Game_classes,
                 work_sort_rule_list: list[WorkSortRule],
                 work_validation_rule_list: list[WorkValidationRule]
                 ):
        """
        Initializes an ExpScriptDataManagerLoader object.

        Args:
            game_classes (Game_classes): An instance of Game_classes containing game-related data.
            work_sort_rule_list (list[WorkSortRule]): A list of WorkSortRule objects for sorting work jobs.
            work_validation_rule_list (list[WorkValidationRule]): A list of WorkValidationRule objects for validating work jobs.
        """
        self.game_classes = game_classes
        self.work_sort_rule_list = work_sort_rule_list
        self.work_validation_rule_list = work_validation_rule_list

    def _load_work_data_loader(self, map: Map) -> WorkDataLoader:
        """
        Loads the WorkDataLoader object.

        Args:
            map (Map): An instance of Map representing the game map.

        Returns:
            WorkDataLoader: An instance of WorkDataLoader for loading work data.
        """
        return WorkDataLoader(handler=self.game_classes.handler,
                              player_data=self.game_classes.player_data,
                              map=map
                              )

    def load(self, map: Map) -> ExpScriptJobDataManager:
        """
        Loads the ExpScriptJobDataManager object.

        Args:
            map (Map): An instance of Map representing the game map.

        Returns:
            ExpScriptJobDataManager: An instance of ExpScriptJobDataManager for managing work jobs.
        """
        return ExpScriptJobDataManager(
            work_data_loader=self._load_work_data_loader(map=map),
            work_sort_rule_list=self.work_sort_rule_list,
            work_validation_rule_list=self.work_validation_rule_list
        )



class ExpScriptLoader:
    """
    Loads an instance of ExpScript, orchestrating the process of selecting and executing work actions.
    """

    def __init__(self,
                 game_classes: Game_classes,
                 job_script_manager_loader: ExpScriptDataManagerLoader,
                 script_selector: ExpScriptJobSelector,
                 map: Map
                 ):
        """
        Initializes an ExpScriptLoader object.

        Args:
            game_classes (Game_classes): An instance of Game_classes containing game-related data.
            job_script_manager_loader (ExpScriptDataManagerLoader): An instance of ExpScriptDataManagerLoader for loading job data.
            script_selector (ExpScriptJobSelector): An instance of ExpScriptJobSelector for selecting work actions.
            map (Map): An instance of Map representing the game map.
        """
        self.game_classes = game_classes
        self.job_script_manager_loader = job_script_manager_loader
        self.script_selector = script_selector
        self.map = map

    def load(self , level :int) -> ExpScript:
        """
        Loads an instance of ExpScript.

        Returns:
            ExpScript: An instance of ExpScript for managing work actions.
        """
        return ExpScript(game_classes=self.game_classes,
                         script_job_manager=self.job_script_manager_loader.load(map=self.map),
                         script_selector=self.script_selector,
                         map=self.map,
                         level = level
                         )


def load_exp_script(game_classes: Game_classes, level : int , max_allowed_damage_percent : float = 0.25 , max_allowed_damage_frequency : float = 0.15) -> ExpScript:
    """
    Loads an instance of ExpScript using the provided Game_classes.

    Args:
        game_classes (Game_classes): An instance of Game_classes containing game-related data.

    Returns:
        ExpScript: An instance of ExpScript for managing work actions based on the provided game data.
    """
    map = MapLoader(
        handler=game_classes.handler,
        player_data=game_classes.player_data,
        work_list=game_classes.work_list
    ).build()

    # Define rules for selecting and validating work jobs
    exp_rule = ExpDamageRule(time_value=15)
    damage_validation_rule = DamageValidationRule(
        handler=game_classes.handler,
        player_data=game_classes.player_data,
        map=map,
        max_allowed_damage_percent=0.25
    )
    frequency_validation_rule = FrequencyDamageValidationRule(
        handler=game_classes.handler,
        player_data=game_classes.player_data,
        map=map,
        max_allowed_damage_frequency=0.15
    )

    # Load ExpScriptDataManagerLoader
    job_script_manager_loader = ExpScriptDataManagerLoader(
        game_classes=game_classes,
        work_sort_rule_list=[exp_rule],
        work_validation_rule_list= []#[damage_validation_rule, frequency_validation_rule]
    )

    # Define ExpScriptJobSelector
    selector = ExpScriptJobSelector(
        duration=15,
        player_data=game_classes.player_data
    )

    # Load ExpScriptLoader
    exp_script_loader = ExpScriptLoader(
        game_classes=game_classes,
        job_script_manager_loader=job_script_manager_loader,
        script_selector=selector,
        map=map
    )

    # Return the loaded ExpScript
    return exp_script_loader.load(level=level)