from dataclasses import dataclass
import typing
import datetime

from script_data import Script_settings

from ..the_west_inner.equipment import Equipment
from ..the_west_inner.game_classes import Game_classes
from ..the_west_inner.gold_finder import parse_map_tw_gold
from ..the_west_inner.crafting import fa_rost
from ..the_west_inner.misc_scripts import recompensaZilnica,wait_until_date
from ..the_west_inner.work_manager import Work_manager
from ..the_west_inner.work import Work
from ..the_west_inner.consumable import Consumable_handler
from ..the_west_inner.bag import Bag
from ..the_west_inner.login import Game_login

class Script_constants():
    OFICIU_JOB_ID:int = 155
    MOTIVATION_CONSUMABLE_ID : int = 1891000
    ENERGY_CONSUMABLE_ID : int = 51594000
    TARGET_PRODUCT : int = 742000
    PRODUCT_EQUIPMENT_W_16 : Equipment = Equipment(
        head_item_id= 52176000 ,
        neck_item_id= 52177000 ,
        left_arm_item_id= 52183000 ,
        body_item_id= 52178000 ,
        right_arm_item_id= 52184000 ,
        foot_item_id= 52181001 ,
        animal_item_id= 52097000 ,
        belt_item_id= 52179000 ,
        pants_item_id = 52180000 ,
        yield_item_id = 52098000
        )
    PRODUCT_EQUIPMENT_W_27 : Equipment = Equipment(
        head_item_id= None ,
        neck_item_id= None ,
        left_arm_item_id= None ,
        body_item_id= None ,
        right_arm_item_id= None ,
        foot_item_id= None ,
        animal_item_id= None ,
        belt_item_id= None ,
        pants_item_id = None ,
        yield_item_id = None
        )
    COMMERCE_EQUIPMENT : Equipment = Equipment(
        head_item_id= None ,
        neck_item_id= None ,
        left_arm_item_id= None ,
        body_item_id= None ,
        right_arm_item_id= None ,
        foot_item_id= None , 
        animal_item_id= None ,
        belt_item_id= None ,
        pants_item_id = None ,
        yield_item_id = None
        )

class Script_work_task:
    """
    Handler the logic required for the caracter to do a number of tasks for a certain Work object

    Args:
        work_manager (Work_manager): The manager responsible for handling work tasks.
        work_data (Work): The specific work data for the task.
        number_of_actions (int): The number of work tasks for this work.
        game_classes (Game_classes): The game-related classes and data.

    Attributes:
        work_manager (Work_manager): The manager responsible for handling work tasks.
        work_data (Work): The specific work data for the task.
        number_of_actions (int): The remaining number of actions to perform for this task.
        game_classes (Game_classes): The game-related classes and data.
    """

    def __init__(self, work_manager: Work_manager, work_data: Work, number_of_actions: int, game_classes: Game_classes):
        self.work_manager = work_manager
        self.work_data = work_data
        self.number_of_actions = number_of_actions
        self.game_classes = game_classes

    def execute(self):
        """
        Execute the work task by performing actions until the number_of_actions reaches zero.
        """
        while self.number_of_actions != 0:
            # Wait until the task queue is empty .
            wait_until_date(self.game_classes.task_queue.get_tasks_expiration(), self.game_classes.handler)

            # Determine the maximum number of tasks allowed
            maximum_number_of_task_allowed = self.work_manager.allowed_tasks()

            # Perform the work for the minimum of maximum allowed tasks and remaining actions
            self.work_manager.work(work_object=self.work_data, number_of_tasks=min(maximum_number_of_task_allowed, self.number_of_actions))

            # Reduce the remaining actions
            self.number_of_actions -= min(maximum_number_of_task_allowed, self.number_of_actions)

        # Wait for the task's expiration time again when the execution of the method is done.
        wait_until_date(self.game_classes.task_queue.get_tasks_expiration(), self.game_classes.handler)


class Ciclu_exp:
    """
    Is an object that handles the logic of working jobs and replenishing energy and motivation .

    Args:
        game_classes (Game_classes): The game-related classes and data.
        job_data (List[Work]): List of work data representing the targeted jobs.
        consumable_handler (Consumable_handler): Handler for consumable items.

    Attributes:
        handler (Handler): The handler for game-related actions.
        job_data (List[Work]): List of work data representing target jobs.
        game_classes (Game_classes): The game-related classes and data.
        work_manager (Work_manager): The manager responsible for handling work tasks.
        consumable_handler (Consumable_handler): Handler for consumable items.
    """

    def __init__(self, game_classes: Game_classes, job_data: typing.List[Work], consumable_handler: Consumable_handler):
        self.handler = game_classes.handler
        self.job_data = job_data
        self.game_classes = game_classes
        self.work_manager = game_classes.work_manager
        self.consumable_handler = consumable_handler

    def _analize_motivation(self) -> typing.List[Script_work_task]:
        """
        Analyze motivation levels and create a list of Script_work_task objects based on available actions.

        Returns:
            List[Script_work_task]: List of work tasks to be executed.
        """
        player_data = self.game_classes.player_data
        player_data.update_character_variables(self.handler)
        energy = player_data.energy
        motivation = self.game_classes.work_list.motivation(self.handler)
        work_tasks_actions = []
        possible_actions = energy

        # Loop through available jobs and motivation levels
        for job in self.job_data:
            if motivation[str(job.job_id)] > 75 and possible_actions != 0:
                actions = min(motivation[str(job.job_id)] - 75, possible_actions)
                possible_actions -= actions

                # Create Script_work_task object with work details
                work_tasks_actions.append(Script_work_task(work_manager=self.work_manager, work_data=job, number_of_actions=actions, game_classes=self.game_classes))

            if possible_actions == 0:
                break

        return work_tasks_actions

    def work_cycle(self, motivation_consumable: int):
        """
        Execute the work tasks cycle based on available motivation and energy.

        Args:
            motivation_consumable (int): The ID of the motivation consumable item.
        """
        work_data = self._analize_motivation()

        if len(work_data) == 0:
            return True

        # Execute work tasks in the cycle
        for work_task in work_data:
            work_task.execute()

        # Recursive call to continue the cycle
        return self.work_cycle(motivation_consumable=motivation_consumable)

    def cycle(self, motivation_consumable: int, energy_consumable: int, number_of_cycles=1):
        """
        Execute the work cycle for a specified number of cycles.

        Args:
            motivation_consumable (int): The ID of the motivation consumable item.
            energy_consumable (int): The ID of the energy consumable item.
            number_of_cycles (int, optional): Number of cycles to perform. Defaults to 1.
        """
        player_data = self.game_classes.player_data
        initial_number_of_cycles = number_of_cycles
        player_data = self.game_classes.player_data
        player_data.update_character_variables(self.handler)
        energy = player_data.energy

        # Use energy consumable if energy is low in the first cycle
        if energy <= 2 and number_of_cycles == 1:
            self.consumable_handler.use_consumable(energy_consumable)
            player_data.update_character_variables(self.handler)

        # Execute work cycles
        while number_of_cycles != 0:
            if energy <= 2 and initial_number_of_cycles == 1:
                break

            if energy <= 2:
                # Use energy consumable to continue cycling
                self.consumable_handler.use_consumable(energy_consumable)
                player_data.update_character_variables(self.handler)
                number_of_cycles -= 1

            # Execute the work cycle and update energy
            solution = self.work_cycle(motivation_consumable=motivation_consumable)
            player_data = self.game_classes.player_data
            player_data.update_character_variables(self.handler)
            energy = player_data.energy

            # Use motivation consumable if cycle was successful and energy is sufficient
            if solution and energy >= 3:
                self.consumable_handler.use_consumable(motivation_consumable)



class Work_cycle_judge:
    """
    Represents a judge that determines whether a work cycle should continue based on specific conditions.

    Args:
        bag (Bag): The player's bag containing items.
        energy_consumable (int): The ID of the energy consumable item.
        motivation_consumable (int): The ID of the motivation consumable item.
        mode (str): The mode of judging cycles ('time' or 'finite_number').
        end_time (datetime.datetime, optional): The end time for time-based judging. Defaults to current time.
        number_of_cycles (int, optional): The number of cycles for finite_number mode. Defaults to 0.

    Attributes:
        bag (Bag): The player's bag containing items.
        energy_consumable (int): The ID of the energy consumable item.
        motivation_consumable (int): The ID of the motivation consumable item.
        mode (str): The mode of judging cycles ('time' or 'finite_number').
        end_time (datetime.datetime): The end time for time-based judging.
        number_of_cycles (int): The remaining number of cycles for finite_number mode.
    """

    def __init__(self, bag: Bag, energy_consumable: int, motivation_consumable: int, mode: str, end_time: datetime.datetime = datetime.datetime.now(), number_of_cycles: int = 0):
        if mode != 'time' and mode != "finite_number":
            raise Exception("Invalid judge type!")

        self.bag = bag
        self.energy_consumable = energy_consumable
        self.motivation_consumable = motivation_consumable
        self.mode = mode
        self.end_time = end_time
        self.number_of_cycles = number_of_cycles

    def consume_cycle(self):
        """Consume a cycle from the remaining cycles (for finite_number mode)."""
        if self.number_of_cycles == 0:
            raise Exception("Can't reduce cycle number below 0")
        self.number_of_cycles -= 1

    def set_cycle_number(self, number: int):
        """Set the remaining number of cycles (for finite_number mode)."""
        if number < 0:
            raise Exception("Cycles can only be set with positive numbers")

    def _time_mode(self) -> bool:
        """Check if the cycle should continue based on time mode."""
        return datetime.datetime.now() < self.end_time

    def _number_of_cycles_mode(self) -> bool:
        """Check if the cycle should continue based on finite_number mode."""
        return self.number_of_cycles > 0

    def should_cycle(self) -> bool:
        """
        Determine whether a cycle should continue based on the chosen mode.

        Returns:
            bool: True if the cycle should continue, False otherwise.
        """
        if self.mode == "time":
            return self._time_mode()

        # For finite_number mode, consume a cycle and return the result
        result = self._number_of_cycles_mode()
        self.consume_cycle()
        return result

class Ciclu_munci:
    """
    Represents a work cycle manager that orchestrates work cycles on a single job based on provided conditions.

    Args:
        game_classes (Game_classes): An instance of the Game_classes class.
        job_data (Work): The work data to be performed in the cycle.
        energy_consummable_id (int): The ID of the energy consumable item.
        motivation_consummable_id (int): The ID of the motivation consumable item.
        cycle_judge (Work_cycle_judge): The cycle judge to determine if cycles should continue.

    Attributes:
        game_classes (Game_classes): An instance of the Game_classes class.
        job_data (Work): The work data to be performed in the cycle.
        energy_consummable_id (int): The ID of the energy consumable item.
        motivation_consummable_id (int): The ID of the motivation consumable item.
        cycle_judge (Work_cycle_judge): The cycle judge to determine if cycles should continue.
    """

    def __init__(self, game_classes: Game_classes, job_data: Work, energy_consummable_id: int, motivation_consummable_id: int, cycle_judge: Work_cycle_judge):
        self.game_classes = game_classes
        self.job_data = job_data
        self.energy_consummable_id = energy_consummable_id
        self.motivation_consummable_id = motivation_consummable_id
        self.cycle_judge = cycle_judge

    def energy_cycle(self):
        """
        Execute work cycles while the cycle judge allows.

        This method manages the execution of work cycles based on the provided cycle judge.
        It initiates work cycles, consumes energy and motivation consumables, and manages cycle duration.

        Returns:
            None
        """
        while self.cycle_judge.should_cycle():
            # Create a Ciclu_exp instance to perform work cycles
            Ciclu_exp(
                game_classes=self.game_classes,
                job_data=[self.job_data],
                consumable_handler=self.game_classes.consumable_handler
            ).cycle(motivation_consumable=self.motivation_consummable_id, energy_consumable=self.energy_consummable_id)


def create_silver_end_time():
    return (datetime.datetime.now() + datetime.timedelta(days=1)).replace(hour=3, minute=0, second=0, microsecond=0)
class Script_secunde():
    """
    Represents a script that executes work cycles for a specific interval of time .

    Args:
        game_classes (Game_classes): An instance of the Game_classes class.
        commerce_equipment (Equipment): The equipment to be used for commerce tasks.
        energy_consummable_id (int): The ID of the energy consumable item.
        motivation_consummable_id (int): The ID of the motivation consumable item.
        luck_bonus_consumable_id (int): The ID of the luck bonus consumable item.
        job_data (Work): The work data to be performed.

    Attributes:
        game_classes (Game_classes): An instance of the Game_classes class.
        commerce_equipment (Equipment): The equipment to be used for commerce tasks.
        energy_consummable_id (int): The ID of the energy consumable item.
        motivation_consummable_id (int): The ID of the motivation consumable item.
        luck_bonus_consumable_id (int): The ID of the luck bonus consumable item.
        job_data (Work): The work data to be performed.
    """

    def __init__(self, game_classes: Game_classes, commerce_equipment: Equipment, energy_consummable_id: int, motivation_consummable_id: int, luck_bonus_consumable_id: int, job_data: Work):
        self.game_classes = game_classes
        self.commerce_equipment = commerce_equipment if commerce_equipment is not None else self.game_classes.equipment_manager.current_equipment
        self.energy_consummable_id = energy_consummable_id
        self.motivation_consummable_id = motivation_consummable_id
        self.luck_bonus_consumable_id = luck_bonus_consumable_id
        self.job_data = job_data

    def execute(self) -> None:
        """
        Execute the script to perform work cycles at specific time intervals.

        This method equips the required equipment, manages cycle intervals using a Work_cycle_judge,
        and performs work cycles using the Ciclu_munci instance.

        Returns:
            None
        """
        self.game_classes.equipment_manager.equip_equipment(equipment=self.commerce_equipment, handler=self.game_classes.handler)
        # Create a cycle judge based on time intervals
        cycle_judge = Work_cycle_judge(
            bag=self.game_classes.bag,
            energy_consumable=self.energy_consummable_id,
            motivation_consumable=self.motivation_consummable_id,
            mode='time',
            end_time=create_silver_end_time()
        )
        # Create a Ciclu_munci instance and perform work cycles
        cycle = Ciclu_munci(
            game_classes=self.game_classes,
            job_data=self.job_data,
            energy_consummable_id=self.energy_consummable_id,
            motivation_consummable_id=self.motivation_consummable_id,
            cycle_judge=cycle_judge
        )
        cycle.energy_cycle()

        
class Script_produse():
    """
    Represents a script that executes product creation tasks.It does not keep you logged in , instead it does hourly tasks .

    Args:
        game_classes (Game_classes): An instance of the Game_classes class.
        products_equipment (Equipment): The equipment to be used for product creation tasks.
        target_mass_product_id (int): The ID of the target mass product.

    Attributes:
        game_classes (Game_classes): An instance of the Game_classes class.
        products_equipment (Equipment): The equipment to be used for product creation tasks.
        target_mass_product_id (int): The ID of the target mass product.
    """

    def __init__(self, game_classes: Game_classes, products_equipment: Equipment, target_mass_product_id: int):
        self.game_classes = game_classes
        self.products_equipment = products_equipment if products_equipment is not None else self.game_classes.equipment_manager.current_equipment
        self.target_mass_product_id = target_mass_product_id

    def execute(self):
        """
        Execute the script to perform product creation tasks.

        This method equips the required equipment, uses the fa_rost function to create products.

        Returns:
            None
        """
        self.game_classes.equipment_manager.equip_equipment(equipment=self.products_equipment, handler=self.game_classes.handler)
        # Use the fa_rost function to create products
        fa_rost(
            id_item=self.target_mass_product_id,
            nr=100,
            game_classes=self.game_classes
        )



@dataclass
class Script_comert_produs_clona:
    """
    Represents a script that alternates between job cycles and product gathering based on my desired parameters .

    Args:
        game_classes (Game_classes): An instance of the Game_classes class.
        energy_consummable_id (int): The ID of the energy consumable item.
        motivation_consummable_id (int): The ID of the motivation consumable item.
        luck_bonus_consumable_id (int): The ID of the luck bonus consumable item.
        target_mass_product_id (int): The ID of the target mass product.
        target_seconds_work_id (int): The ID of the target seconds work.
        products_equipment (Equipment, optional): The equipment for product creation tasks. Defaults to None.
        commerce_equipment (Equipment, optional): The equipment for commerce tasks. Defaults to None.
        work_flag (bool, optional): Flag indicating if commerce tasks are enabled. Defaults to False.
    """

    game_classes: Game_classes
    energy_consummable_id: int
    motivation_consummable_id: int
    luck_bonus_consumable_id: int
    target_mass_product_id: int
    target_seconds_work_id: int
    products_equipment: Equipment = None
    commerce_equipment: Equipment = None
    work_flag: bool = False

    def _available_silver_job(self):
        """
        Get the available silver job based on target_seconds_work_id.

        Returns:
            dict or None: Information about the available silver job, or None if not found.
        """
        silver_jobs = [x for x in parse_map_tw_gold(handler=self.game_classes.handler) if x['job_id'] == self.target_seconds_work_id]
        return silver_jobs[0] if len(silver_jobs) != 0 else None

    def choose_path(self):
        """
        Choose the appropriate script path based on work_flag and available silver job.

        Returns:
            Script_secunde or Script_produse: Instance of the chosen script.
        """
        recompensaZilnica(handler=self.game_classes.handler)

        if self.work_flag:
            available_silver_job = self._available_silver_job()
            if available_silver_job:
                # Create Work instance based on available silver job
                job_data = Work(job_id=self.target_seconds_work_id, x=available_silver_job['x'], y=available_silver_job['y'], duration=15)
                # Choose Script_secunde for commerce tasks
                return Script_secunde(
                    game_classes=self.game_classes,
                    commerce_equipment=self.commerce_equipment,
                    energy_consummable_id=self.energy_consummable_id,
                    motivation_consummable_id=self.motivation_consummable_id,
                    luck_bonus_consumable_id=self.luck_bonus_consumable_id,
                    job_data=job_data
                )
        # Choose Script_produse for product creation tasks
        return Script_produse(
            game_classes=self.game_classes,
            products_equipment=self.products_equipment,
            target_mass_product_id=self.target_mass_product_id
        )

    def execute(self):
        """
        Execute the chosen script path.

        Returns:
            None
        """
        chosen_script = self.choose_path()
        chosen_script.execute()



def world_script_instance(script_settings: Script_settings):
    """
    Create and execute the world script instance based on the provided settings.

    Args:
        script_settings (Script_settings): An instance of the Script_settings class.

    Returns:
        None
    """
    # Initialize the Game_login instance with the provided credentials
    game = Game_login(player_name=script_settings.name, player_password=script_settings.password, world_id=script_settings.world_id)
    game_data = game.login()

    # Ensure daily rewards are collected
    recompensaZilnica(handler=game_data.handler)

    # Determine whether to use work or product equipment
    if script_settings.work_flag:
        work_equipment = script_settings.work_equipment
        product_equipment = script_settings.product_equipment
    else:
        work_equipment, product_equipment = None, None

    # Create an instance of Script_comert_produs_clona based on the provided settings
    script = Script_comert_produs_clona(
        game_classes=game_data,
        energy_consummable_id=script_settings.energy_consumable,
        motivation_consummable_id=script_settings.motivation_consumable,
        luck_bonus_consumable_id=script_settings.luck_bonus_consumable,
        target_mass_product_id=script_settings.target_product_id,
        target_seconds_work_id=script_settings.target_desired_job_id,
        products_equipment=product_equipment,
        commerce_equipment=work_equipment,
        work_flag=script_settings.work_flag
    )

    # Execute the chosen script path
    script.choose_path().execute()
