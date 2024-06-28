
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


def make_exp_script_executor(callback_chainer : CallbackChainer | None = None ) -> ExpScriptExecutor:
    """
    Creates an instance of ExpScriptExecutor configured with appropriate callback functions.

    Args:
        callback_chainer (CallbackChainer): An instance of CallbackChainer containing the callback functions the executor uses.

    Returns:
        ExpScriptExecutor: An instance of ExpScriptExecutor configured with callback functions.
    """
    # Create and return an instance of ExpScriptExecutor
    return ExpScriptExecutor(script_chainer=callback_chainer)
