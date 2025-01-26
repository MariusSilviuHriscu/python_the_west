from the_west_inner.player_data import Player_data, ClassTypeEnum
from the_west_inner.requests_handler import requests_handler

def set_class_to_adventurer(player_data: Player_data, handler: requests_handler):
    """
    Sets the player's class to Adventurer.

    This function changes the player's class to Adventurer using the provided player data and requests handler.

    Args:
        player_data (Player_data): An instance of Player_data containing the player's information and methods.
        handler (requests_handler): An instance of requests_handler for managing HTTP requests to the game server.

    Returns:
        None
    """
    return
    player_data.select_class(
        handler=handler,
        class_type_enum=ClassTypeEnum.ADVENTURER
    )
