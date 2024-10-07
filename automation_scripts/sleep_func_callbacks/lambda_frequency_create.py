"""
Helper Functions for Callable Rules

This module provides helper functions for creating callable functions used in CallableRunRule.
The generated callable functions serve as conditions for the execution of certain actions or rules.

Functions:
- make_check_health_funct(health_percentage: float, game_classes: Game_classes) -> Callable[[], bool]:
    Creates a callable function to check if the player's health is below a certain percentage.

- make_check_inventory_item_func(item_id: int, item_number: int, game_classes: Game_classes) -> Callable[[], bool]:
    Creates a callable function to check if the player's inventory has a certain number of a specific item.
"""
import typing
from the_west_inner.game_classes import Game_classes
from the_west_inner.player_data import ClassTypeEnum

def make_check_health_funct(health_percentage: float, game_classes: Game_classes) -> typing.Callable[[], bool]:
    """
    Creates a callable function to check if the player's health is below a certain percentage.

    Args:
    - health_percentage (float): The threshold percentage for health.
    - game_classes (Game_classes): An instance of the Game_classes containing player data.

    Returns:
    Callable[[], bool]: A function that checks if the player's health is below the specified percentage.
    """
    def check_health() -> bool:
        """
        Checks if the player's health is below a certain percentage.

        Returns:
        bool: True if health is below the specified percentage, False otherwise.
        """
        game_classes.player_data.update_character_variables(handler=game_classes.handler)
        return game_classes.player_data.hp * 1.0 / game_classes.player_data.hp_max < health_percentage

    return check_health

def make_check_inventory_item_func(item_id: int, item_number: int, game_classes: Game_classes)-> typing.Callable[[], bool]:
    """
    Creates a callable function to check if the player's inventory has a certain number of a specific item.

    Args:
    - item_id (int): The ID of the item to check in the inventory.
    - item_number (int): The required number of the item in the inventory.
    - game_classes (Game_classes): An instance of the Game_classes containing player's inventory.

    Returns:
    Callable[[], bool]: A function that checks if the player's inventory has the required number of the specified item.
    """
    def check_inventory_item() -> bool:
        """
        Checks if the player's inventory has a certain number of a specific item.

        Returns:
        bool: True if the required number of the specified item is in the inventory, False otherwise.
        """
        return game_classes.bag[item_id] >= item_number

    return check_inventory_item

def make_check_if_can_change_class(game_classes : Game_classes) -> typing.Callable[[],bool]:
    
    
    def check_if_can_change() -> bool:
        
        return game_classes.player_data.level >= 15 and ClassTypeEnum.GREENHORN.value == game_classes.player_data.class_key
    
    return check_if_can_change
