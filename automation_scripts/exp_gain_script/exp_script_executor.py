
from the_west_inner.game_classes import Game_classes

from automation_scripts.exp_gain_script.exp_script import ExpScript
from automation_scripts.sleep_func_callbacks.callback_chain import CallbackChainer
from automation_scripts.sleep_func_callbacks.misc_func_callback import check_and_update_skills

class ExpScriptExecutor:
    """
    Executes an instance of ExpScript by chaining callback functions.

    Args:
        script_chainer (CallbackChainer): An instance of CallbackChainer to chain callback functions.
    """

    def __init__(self, script_chainer: CallbackChainer):
        """
        Initializes the ExpScriptExecutor with the provided CallbackChainer.

        Args:
            script_chainer (CallbackChainer): An instance of CallbackChainer.
        """
        self.script_chainer = script_chainer

    def execute(self, exp_script: ExpScript):
        """
        Executes the given ExpScript by cycling through work actions and applying callback functions.

        Args:
            exp_script (ExpScript): An instance of ExpScript to execute.
        """
        exp_script.cycle_exp(callback_function=self.script_chainer.chain_function())


def make_exp_script_executor(game_classes: Game_classes):
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

    # Create and return an instance of ExpScriptExecutor
    return ExpScriptExecutor(script_chainer=chainer)
