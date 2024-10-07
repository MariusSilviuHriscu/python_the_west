from the_west_inner.game_classes import Game_classes
from the_west_inner.map import MapLoader
from the_west_inner.work_job_data import ExpDamageRule, DamageValidationRule, FrequencyDamageValidationRule

from automation_scripts.exp_gain_script.exp_script_load import ExpScriptDataManagerLoader, ExpScriptLoader
from automation_scripts.exp_gain_script.exp_script import ExpScriptJobSelector, ExpScript
from automation_scripts.exp_gain_script.exp_script_executor import ExpScriptExecutor

from automation_scripts.sleep_func_callbacks.callback_chain import CallbackChainer
from automation_scripts.sleep_func_callbacks.callback_frequency import CallableRunRule

from automation_scripts.sleep_func_callbacks.misc_func_callback import check_and_update_skills
from automation_scripts.sleep_func_callbacks.class_select import  set_class_to_adventurer

from automation_scripts.sleep_func_callbacks.lambda_frequency_create import make_check_if_can_change_class

def load_exp_script_v1(game_classes: Game_classes, level: int, max_allowed_damage_percent: float = 0.25, max_allowed_damage_frequency: float = 0.15) -> ExpScript:
    """
    Loads an instance of ExpScript using the provided Game_classes.

    Args:
        game_classes (Game_classes): An instance of Game_classes containing game-related data.
        level (int): The level at which to load the ExpScript.
        max_allowed_damage_percent (float, optional): Maximum allowed damage percentage for validation. Defaults to 0.25.
        max_allowed_damage_frequency (float, optional): Maximum allowed damage frequency for validation. Defaults to 0.15.

    Returns:
        ExpScript: An instance of ExpScript for managing work actions based on the provided game data.
    """
    # Initialize the game map
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
        max_allowed_damage_percent=max_allowed_damage_percent
    )
    frequency_validation_rule = FrequencyDamageValidationRule(
        handler=game_classes.handler,
        player_data=game_classes.player_data,
        map=map,
        max_allowed_damage_frequency=max_allowed_damage_frequency
    )

    # Load ExpScriptDataManagerLoader with rules
    job_script_manager_loader = ExpScriptDataManagerLoader(
        game_classes=game_classes,
        work_sort_rule_list=[exp_rule],
        work_validation_rule_list=[damage_validation_rule, frequency_validation_rule]
    )

    # Define ExpScriptJobSelector with a specified duration
    selector = ExpScriptJobSelector(
        duration=15,
        player_data=game_classes.player_data
    )

    # Load ExpScriptLoader with the manager loader and selector
    exp_script_loader = ExpScriptLoader(
        game_classes=game_classes,
        job_script_manager_loader=job_script_manager_loader,
        script_selector=selector,
        map=map
    )

    # Return the loaded ExpScript
    return exp_script_loader.load(level=level)

def make_exp_script_executor_v1(game_classes: Game_classes ,
                                additional_chainer :CallbackChainer|None= None
                                ) -> ExpScriptExecutor:
    """
    Creates an instance of ExpScriptExecutor configured with appropriate callback functions.

    Args:
        game_classes (Game_classes): An instance of Game_classes containing game-related data.

    Returns:
        ExpScriptExecutor: An instance of ExpScriptExecutor configured with callback functions.
    """
    # Initialize a CallbackChainer
    chainer = CallbackChainer()

    # Add callback function to update skills
    chainer.add_callback(
        callback_function=check_and_update_skills,
        handler=game_classes.handler,
        target_attribute_key='strength',
        target_skill_key='build'
    )

    # Add callback function to update the player's class to adventurer
    chainer.add_callback(
        callback_function=set_class_to_adventurer,
        player_data=game_classes.player_data,
        handler=game_classes.handler
    )

    # Create a CallableRunRule for conditional execution of class change check
    rule = CallableRunRule(
        condition_callable=make_check_if_can_change_class(game_classes=game_classes)
    )

    # Set the frequency rule for the chainer
    chainer.set_frequency(rule=rule)
    
    
    chainer.add_default_kwargs(game_classes = game_classes)
    
    if additional_chainer is not None:
        
        
        chainer = additional_chainer + chainer

    # Create and return an instance of ExpScriptExecutor with the configured chainer
    return ExpScriptExecutor(script_chainer=chainer)
