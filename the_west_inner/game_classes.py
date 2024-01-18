from dataclasses import dataclass
from requests_handler import requests_handler
from movement import Game_data
from player_data import Player_data
from task_queue import TaskQueue
from premium import Premium
from work_list import Work_list
from items import Items
from crafting import Crafting_table, Crafting
from bag import Bag
from work_manager import Work_manager
from consumable import Consumable_handler,Cooldown
from equipment import Equipment_manager
from buffs import Buff_list
from currency import Currency
from movement_manager import MovementManager

"""
This module contains the GameClasses dataclass, which holds instances of various classes used to manage gameplay in a game. The handler attribute is an instance of the RequestsHandler class, which is used to send HTTP requests to the game's API. The game_data attribute is an instance of the GameData class, which holds data about the game world. The player_data attribute is an instance of the PlayerData class, which holds data about the player character. The task_queue attribute is an instance of the TaskQueue class, which is used to queue up tasks for the character to perform. The premium attribute is an instance of the Premium class, which holds data about the player's premium status. The work_list attribute is an instance of the WorkList class, which holds a list of available jobs in the game. The items attribute is an instance of the Items class, which is used to handle item-related gameplay. The crafting_table attribute is an instance of the CraftingTable class, which is used to interact with the crafting table in the game. The player_crafting attribute is an instance of the Crafting class, which is used to craft items. The bag attribute is an instance of the Bag class, which is used to store items. The cooldown attribute is an instance of the Cooldown class, which is used to manage cooldown periods for certain actions. The work_manager attribute is an instance of the WorkManager class, which is used to manage work-related gameplay. The consumable_handler attribute is an instance of the ConsumableHandler class, which is used to handle consumable items.
"""

@dataclass
class Game_classes():
    handler: requests_handler
    game_data: Game_data
    player_data : Player_data
    task_queue : TaskQueue
    premium : Premium
    work_list : Work_list
    items : Items
    crafting_table :Crafting_table #'typing.Any'
    player_crafting :Crafting #'typing.Any'
    bag : Bag
    cooldown : Cooldown
    buff_list : Buff_list
    work_manager : Work_manager
    consumable_handler : Consumable_handler
    equipment_manager : Equipment_manager
    currency : Currency
    movement_manager : MovementManager