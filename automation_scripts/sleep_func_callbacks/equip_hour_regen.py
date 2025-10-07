from automation_scripts.notebook_storage.equipment_changer import build_notebook_changer, NotebookChanger
from the_west_inner.equipment import Equipment
from the_west_inner.game_classes import Game_classes


def change_regen(game_classes: Game_classes, regen_equip: Equipment):
    """
    Changes equipment based on current energy levels and queued tasks.
    """

    # Build the notebook changer
    changer = build_notebook_changer(game_classes=game_classes, regen_equip=regen_equip)

    # Do nothing if multiple tasks are queued
    if len(game_classes.task_queue) > 1:
        return

    energy = game_classes.player_data.energy
    max_energy = game_classes.player_data.energy_max
    handler = game_classes.handler
    task_queue = game_classes.task_queue

    # If there are no active tasks (assuming we can check emptiness)
    if not task_queue:
        if energy < 12:
            changer.equip_regen(handler=handler)
        else:
            changer.equip_work(handler=handler)
        return

    # If a sleep task is in the queue
    if task_queue.sleep_task_in_queue():
        if energy < max_energy:
            changer.equip_regen(handler=handler)
        else:
            changer.equip_work(handler=handler)
