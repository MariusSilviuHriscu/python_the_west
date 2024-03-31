import typing

from the_west_inner.game_classes import Game_classes

from automation_scripts.exp_gain_script.exp_script import ExpScript
from automation_scripts.sleep_func_callbacks.callback_chain import CallbackChainer
from automation_scripts.sleep_func_callbacks.misc_func_callback import check_and_update_skills

class ExpScriptExecutor:
    
    def __init__(self ,
                 script_chainer : CallbackChainer ) :

        self.script_chainer = script_chainer
    
    
    def execute( self , exp_script: ExpScript ) :
        
        exp_script.cycle_exp(callback_function= self.script_chainer)
    


def make_exp_script_executor(game_classes : Game_classes):
    
    chainer = CallbackChainer()
    
    chainer.add_callback(callback_function=check_and_update_skills ,
                         handler = game_classes.handler ,
                         target_attribute_key = 'strength',
                         target_skill_key = 'build'
                         )
    
    return ExpScriptExecutor(script_chainer = chainer)