from requests_handler import requests_handler
from task_queue import TaskQueue
from premium import Premium
from player_data import Player_data
from work_list import Work_list
from work import get_closest_workplace_data, munceste_coord
from misc_scripts import sleep_closest_town
from items import Items,get_corresponding_work_id
from dataclasses import dataclass

"""
This module contains classes and functions for handling crafting in a game. The `Crafting` class is used to craft items, while the `craft_item` function is used to craft the specified item using the `Crafting` class.

The `Crafting` class has the following attributes:
    - handler (requests_handler): A request handler.
    - items (Items): An instance of the Items class.
    - premium (Premium): An instance of the Premium class.
    - player_data (Player_data): An instance of the Player_data class.
    - work_list (Work_list): An instance of the Work_list class.

The `Crafting` class has the following methods:
    - craft: Crafts the specified item.

The `craft_item` function takes the following arguments:
    - item_id (int): The ID of the item to craft.
    - handler (requests_handler): A request handler.
    - items (Items): An instance of the Items class.
    - premium (Premium): An instance of the Premium class.
    - player_data (Player_data): An instance of the Player_data class.
    - work_list (Work_list): An instance of the Work_list class.
"""
            

def product_hourly_work(job_id,handler:requests_handler,task_queue:TaskQueue,premium:Premium,player_data:Player_data,work_list:Work_list):
    nr_munci = task_queue.get_tasks_number()
    if task_queue.sleep_task_in_queue():
        if player_data.energy == player_data.energy_max:
            task_queue.tasks.cancel()
        else:
            return
    has_premium = premium.automation
    nr_max = 4
    if has_premium :
        nr_max = 9
    nr_max = nr_max - task_queue.get_tasks_number()
    nr_max_energy = player_data.energy // 12
    if nr_max_energy < nr_max:
        munca = get_closest_workplace_data(handler = handler,
                                job_id=job_id,
                                job_list= work_list,
                                player_data= player_data
                                )
        for i in range(nr_max_energy):
            munceste_coord.ore(munca,handler)
        sleep_closest_town(handler=handler,player_data= player_data)
    else:
        munca = get_closest_workplace_data(handler = handler,
                                job_id=job_id,
                                job_list= work_list,
                                player_data= player_data
                                )
        for i in range(nr_max):
            munceste_coord.ore(munca,handler)
class OneHourProductWorker:
    def __init__(self, handler: requests_handler, task_queue: TaskQueue, premium: Premium, player_data: Player_data, work_list: Work_list):
        self.handler = handler
        self.task_queue = task_queue
        self.premium = premium
        self.player_data = player_data
        self.work_list = work_list

    def must_continue_sleep(self):
        """
        Check if the character is currently sleeping and should continue sleeping.
        """
        if self.task_queue.sleep_task_in_queue():
            if self.player_data.energy == self.player_data.energy_max:
                self.task_queue.tasks.cancel()
            else:
                return True
        return False

    def get_max_nr_of_tasks(self):
        max_nr_of_tasks = 4
        if self.premium.automation:
            max_nr_of_tasks = 9
        return max_nr_of_tasks - self.task_queue.get_tasks_number()

    def get_coordinates(self, job_id):
        return get_closest_workplace_data(
            handler=self.handler,
            job_id=job_id,
            job_list=self.work_list,
            player_data=self.player_data,
        )

    def work(self):
        # Check if the player is currently sleeping
        if self.must_continue_sleep():
            return
    
        # Get the maximum number of tasks that can be performed
        max_nr_of_tasks = self.get_max_nr_of_tasks()
    
        # Get the maximum number of tasks that can be performed based on available energy
        max_nr_of_tasks_energy = self.player_data.energy // 12
    
        # Perform tasks
        work_list = self.work_list.work_products()
        if max_nr_of_tasks_energy < max_nr_of_tasks:
            coordinates = self.get_coordinates(work_list["product_id"])
            for _ in range(max_nr_of_tasks_energy):
                munceste_coord.ore(coordinates, self.handler)
            sleep_closest_town(handler=self.handler, player_data=self.player_data)
        else:
            coordinates = self.get_coordinates(work_list["product_id"])
            for _ in range(max_nr_of_tasks):
                munceste_coord.ore(coordinates, self.handler)


@dataclass
class Crafting_recipe():
    recipe_id : int
    craftable : int
    resources : dict
    profession : str
    profession_id : int
class Crafting_table():
    """
    Class that represents the crafting table.
    """
    def __init__(self, items: Items):
        """
        Initializes a new instance of the `Crafting_table` class.
        Args:
            items (Items): The items used to construct the crafting table.
        """
        self.crafting_dict = self._construct_table(items=items)
    def _construct_table(self, items: Items):
        """
        Constructs the crafting table.
    
        Args:
            items (Items): The items used to construct the crafting table.
        Returns:
            dict: The crafting table.
        """
        crafting_dict = {}
        for item in items.items.values():
            if "craftitem" in item:
                recipe_id = item["item_id"]
                craftable = item["craftitem"]
                resources = [x for x in item["resources"]]
                profession = item["profession"]
                profession_id = item["profession_id"]
                crafting_dict[craftable] = Crafting_recipe(
                    recipe_id=recipe_id,
                    craftable=craftable,
                    resources=resources,
                    profession=profession,
                    profession_id=profession_id,
                )
        return crafting_dict
    
    def __getitem__(self, item_id: int):
        """
        Gets the crafting recipe with the specified ID.
    
        Args:
            item_id (int): The ID of the crafting recipe to get.
    
        Returns:
            Crafting_recipe: The crafting recipe with the specified ID.
        """
        return self.crafting_dict[item_id]
    
    def __contains__(self, item_id):
        """
        Determines whether the crafting table contains a crafting recipe with the specified ID.
    
        Args:
            item_id (int): The ID of the crafting recipe to search for.
    
        Returns:
            bool: `True` if the crafting table contains a crafting recipe with the specified ID, `False` otherwise.
        """
        return item_id in self.crafting_dict

class Crafting():
    def __init__(self, crafting_table: Crafting_table, handler: requests_handler):
        """
        Initialize a `Crafting` object with a `Crafting_table` object and a `requests_handler` object.

        :param crafting_table: A `Crafting_table` object representing the available crafting recipes.
        :type crafting_table: Crafting_table
        :param handler: A `requests_handler` object used to make requests to the server.
        :type handler: requests_handler
        """
        self.handler = handler
        self.crafting_table = crafting_table
        self.player_recipes = self._update_player_recipes(handler)

    def _player_crafting(self) -> dict:
        """
        Retrieve the player's available crafting recipes.

        :return: A dictionary containing the player's available crafting recipes.
        :rtype: dict
        """
        crafting_recipes =  self.handler.post(window="crafting", action="")
        return crafting_recipes["recipes_content"]

    def _update_player_recipes(self, handler: requests_handler) -> dict:
        """
        Update the player's available crafting recipes.

        :param handler: A `requests_handler` object used to make requests to the server.
        :type handler: requests_handler
        :return: A dictionary mapping item IDs to `Recipe` objects representing the player's available recipes.
        :rtype: dict
        """
        recipes_ids = [x["item_id"] for x in self._player_crafting()]
        player_recipes = {}
        for recipe_id in recipes_ids:
            for recipe in self.crafting_table.crafting_dict.values():
                if recipe.recipe_id == recipe_id:
                    player_recipes[recipe.craftable] = recipe
        return player_recipes

    def craft(self, item_id: int, number: int) -> dict:
        """
        Craft a specified number of items with the given ID.

        :param item_id: The ID of the item to craft.
        :type item_id: int
        :param number: The number of items to craft.
        :type number: int
        :return: A dictionary containing the result of the crafting action.
        :rtype: dict
        :raises Exception: If the specified item ID is not a valid recipe or if there is an error during crafting.
        """
        if item_id not in self.crafting_table or item_id not in self.player_recipes:
            raise Exception("Not a valid recipe")
        crafting_recipe = self.player_recipes[item_id]
        craft_report = self.handler.post("crafting", "start_craft", payload={"recipe_id": crafting_recipe.recipe_id, "amount": number}, use_h=True)
        if craft_report["error"] == True:
            raise Exception(f"{craft_report['msg']}")
        print(f"{craft_report['msg']}")
        return craft_report

def acquire_product(id_item:int,nr:int,game_classes):
    # Create an instance of the OneHourProductWorker class
    #worker = OneHourProductWorker(
    #    handler=game_classes.handler,
    #    task_queue=game_classes.task_queue,
    #    premium=game_classes.premium,
    #    player_data=game_classes.player_data,
    #    work_list=game_classes.work_list
    #)

    if id_item in game_classes.crafting_table and game_classes.crafting_table[id_item].profession == game_classes.player_data.profession:
        resource_list = game_classes.crafting_table[id_item]
        can_be_crafted = True
        for ingredient in resource_list.resources:
            nr_inv = game_classes.bag[ingredient['item']]
            if nr_inv < ingredient['count'] * nr:
                can_be_crafted = acquire_product(ingredient['item'],nr * ingredient['count']-nr_inv,game_classes)
                if not can_be_crafted:
                    break
        if can_be_crafted:
            game_classes.player_crafting.craft(id_item,nr)
            return True
        return False
    if id_item in game_classes.crafting_table and game_classes.crafting_table[id_item].profession != game_classes.player_data.profession:
        print("Nu se poate crafta :" + game_classes.items(id_item).name())
        return False
    if not (id_item in game_classes.crafting_table):
        product_hourly_work(job_id= get_corresponding_work_id(id_item,work_list=game_classes.work_list) ,
                handler=game_classes.handler,
                task_queue=game_classes.task_queue,
                premium= game_classes.premium,
                player_data= game_classes.player_data,
                work_list= game_classes.work_list
                )

    return False
