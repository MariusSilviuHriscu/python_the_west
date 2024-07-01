import typing
import time
from requests.exceptions import ConnectionError

from the_west_inner.login import Game_login
from the_west_inner.game_classes import Game_classes
from the_west_inner.equipment import Equipment, Equipment_manager
from the_west_inner.requests_handler import requests_handler

from automation_scripts.exp_gain_script.exp_script import ExpScript
from automation_scripts.exp_gain_script.exp_script_executor import ExpScriptExecutor

from automation_scripts.exp_gain_script.example_exp_scripts.loader_func_v1 import load_exp_script_v1, make_exp_script_executor_v1
from automation_scripts.exp_gain_script.example_exp_scripts.sleep_func_v1 import CycleSleeperManager

class CycleScriptEquipmentChanger:
    
    def __init__(self , 
                 regen_equip : Equipment ,
                 work_equip : Equipment 
                 ):
        self.regen_equip = regen_equip
        self.work_equip = work_equip
    
    def equip_regen_equipment(self , 
                              equipment_manager : Equipment_manager ,
                              handler : requests_handler) -> None:
        
        equipment_manager.equip_equipment(equipment = self.regen_equip,
                                          handler = handler
                                          )
    def equip_work_equipment(self , 
                              equipment_manager : Equipment_manager ,
                              handler : requests_handler) -> None:
        
        equipment_manager.equip_equipment(equipment = self.work_equip,
                                          handler = handler)

class CycleScript:
    """
    Manages the execution of an experience script (ExpScript) and its executor (ExpScriptExecutor).
    Handles reconnection and re-execution in case of connection errors.

    Attributes:
        exp_script (ExpScript): The experience script to be executed.
        exp_script_executor (ExpScriptExecutor): The executor that runs the experience script.
    """
    
    def __init__(self, exp_script: ExpScript, exp_script_executor: ExpScriptExecutor):
        """
        Initializes the CycleScript with the provided experience script and executor.

        Args:
            exp_script (ExpScript): The experience script to be executed.
            exp_script_executor (ExpScriptExecutor): The executor that runs the experience script.
        """
        self.exp_script = exp_script
        self.exp_script_executor = exp_script_executor
    
    def set_exp_script(self, exp_script: ExpScript):
        """
        Sets a new experience script.

        Args:
            exp_script (ExpScript): The new experience script to be set.
        """
        self.exp_script = exp_script

    def set_exp_script_executor(self, exp_script_executor: ExpScriptExecutor):
        """
        Sets a new experience script executor.

        Args:
            exp_script_executor (ExpScriptExecutor): The new experience script executor to be set.
        """
        self.exp_script_executor = exp_script_executor

    def execute(self) -> typing.Generator[bool, None, None]:
        """
        Executes the experience script using the executor. Handles reconnection on connection errors.

        Yields:
            bool: True if the cycle starts successfully or finishes without errors, False on connection error.
        """
        flag = True
        while flag:
            try:
                self.exp_script_executor.execute(self.exp_script)
                flag = False
            except ConnectionError:
                yield False
            except Exception as e:
                raise e
        yield True

class CycleScriptManager:
    """
    Manages the creation and execution of CycleScript instances. Handles login and reinitialization of scripts.

    Attributes:
        game_login (Game_login): The login manager for the game.
    """
    
    def __init__(self, game_login: Game_login , equipment_changer : typing.Optional[CycleScriptEquipmentChanger] = None):
        """
        Initializes the CycleScriptManager with the provided login manager.

        Args:
            game_login (Game_login): The login manager for the game.
        """
        self.game_login = game_login
        self.equipment_changer = equipment_changer
        self.current_cycle_script = None
    @property
    def game_data(self) -> Game_classes:
        """
        Logs into the game and retrieves the game data.

        Returns:
            Game_classes: The logged-in game data.
        """
        return self.game_login.login()
    
    def create_cycle_script(self, level: int, game_data: Game_classes) -> CycleScript:
        """
        Creates a new CycleScript instance for the specified level using the provided game data.

        Args:
            level (int): The level for which the cycle script is created.
            game_data (Game_classes): The game data required to create the script.

        Returns:
            CycleScript: The created CycleScript instance.
        """
        exp_script = load_exp_script_v1(game_classes=game_data, level=level)
        exp_script_executor = make_exp_script_executor_v1(game_classes=game_data)
        return CycleScript(exp_script=exp_script, exp_script_executor=exp_script_executor)
    
    def restore_cycle_script(self, level: int, game_data: Game_classes , current_cycle_script: CycleScript):
        """
        Restores the current CycleScript by creating a new one and updating the script and executor.

        Args:
            level (int): The level for which the cycle script is restored.
            game_data (Game_classes): The game data required to create the script.
        """
        new_cycle_script = self.create_cycle_script(level=level, game_data=game_data)
        current_cycle_script.set_exp_script(new_cycle_script.exp_script)
        current_cycle_script.set_exp_script_executor(new_cycle_script.exp_script_executor)

    def _execute_cycle_script(self, level: int, game_data: Game_classes):
        """
        Executes the cycle script, handling reconnection if necessary.

        Args:
            level (int): The level for which the cycle script is executed.
            game_data (Game_classes): The game data required to execute the script.
        """
        cycle = self.create_cycle_script(level=level, game_data=game_data)
        cycle_generator = cycle.execute()
        for cycle_flag in cycle_generator:
            if not cycle_flag:
                self.restore_cycle_script(level=level, game_data=game_data , current_cycle_script=cycle)
    
    def execute_cycle_script(self, level: int):
        """
        Manages the execution of the cycle script and the sleeping cycle.

        Args:
            level (int): The level for which the cycle script is executed.
        """
        game_data = self.game_data
        sleep_manager = CycleSleeperManager(handler=game_data.handler,
                                            task_queue=game_data.task_queue,
                                            work_manager=game_data.work_manager,
                                            player_data=game_data.player_data)
        
        if self.equipment_changer is not None:
            self.equipment_changer.equip_work_equipment(
                    equipment_manager = game_data.equipment_manager,
                    handler = game_data.handler
                )

        if sleep_manager.start_cycle(exp_script=load_exp_script_v1(game_classes=game_data, level=level)):
                                
            self._execute_cycle_script(level=level, game_data=game_data)
            sleep_manager.finish_cycle()
            print('Cycle script finished')
        else:
            print('Cycle finished but did no work!')
        
        if self.equipment_changer is not None:
            self.equipment_changer.equip_regen_equipment(
                    equipment_manager = game_data.equipment_manager,
                    handler = game_data.handler
                )
    def cycle(self, level: int ) -> typing.Generator[None, None, None]:
        """
        Executes the cycle script and sleeps for a specified duration before repeating.

        Args:
            level (int): The level for which the cycle script is executed.
        """
        while True:
            self.execute_cycle_script(level=level)
            time.sleep(3600 / 4)
            yield

