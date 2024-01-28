"""
This module handles functions related to time manipulation, daily rewards, and managing towns in the game.

Functions:
- server_time(handler:requests_handler) -> datetime: Returns the server time.
- wait_until_date(wait_time: datetime, handler:requests_handler) -> bool: Waits until the specified date is reached.
- collect_daily_reward(handler:requests_handler) -> bool: Collects the daily reward.
- get_closest_viable_town(handler:requests_handler, player_data) -> list: Returns the ID, x coordinate, and y coordinate of the town that is closest to the player's location and has a level 5 hotel.
- number_of_tasks(handler:requests_handler) -> int: Returns the number of tasks in the task queue.
- distance_to(target_coords, player_data) -> float: Calculates the distance between the player and a given set of coordinates.
"""
from requests_handler import requests_handler
import time
import datetime
from urllib.parse import urlparse

def server_time(handler:requests_handler) -> datetime:
    """
    This function returns the server time.

    Args:
    handler (requests_handler): The request handler to use for sending requests.

    Returns:
    datetime: The server time.
    """
    d = handler.session.post(
        urlparse(handler.base_url)._replace(path="ntp.php").geturl(), allow_redirects=False
    )
    game_time = time.ctime(float(d.text)/1000)
    game_time = datetime.datetime.strptime(game_time, "%c")
    return game_time


def wait_until_date(wait_time: datetime, handler:requests_handler) -> bool:
    """
    This function waits until the specified date is reached.

    Args:
    wait_time (datetime): The time to wait until.
    handler (requests_handler): The request handler to use for sending requests.

    Returns:
    bool: True if the specified date was reached, False otherwise.
    """
    if wait_time == -1:
        return True

    time_now = datetime.datetime.now()
    if time_now < wait_time:
        delta = (wait_time - time_now).seconds
        print(f'waiting time is " {wait_time} while time now :{time_now}.Delta is :{delta}')
        if delta > 0:
            time.sleep(delta)

    while server_time(handler=handler) < wait_time:
        time.sleep(1)

    return True


def collect_daily_reward(handler:requests_handler):
    succes = handler.post("loginbonus","collect",use_h = True)
    return succes["error"] == False
def distance_to(target_coords,player_data):
    return player_data.absolute_distance_to(target_coords)
def get_closest_viable_town(handler:requests_handler, player_data):
    """
    Returns the ID, x coordinate, and y coordinate of the town that is closest to the player's location
    and has a level 5 hotel.
    
    Args:
        handler: The API handler.
        player_data: The player's location and other relevant data.
    
    Returns:
        A list containing the ID, x coordinate, and y coordinate of the town with a level 5 hotel,
        or None if no such town exists.
    """
    # Make an API call to get the minimap data.
    response = handler.post("map", "get_minimap", action_name="ajax")
    
    # Extract the dictionary of towns from the response.
    towns = response["towns"]
    
    # Create a list to store the towns that have members.
    viable_towns = []
    
    # Iterate through the towns and add the towns with members to the viable_towns list.
    for town in towns.values():
        if int(town["member_count"]) != 0:
            town_data = [town["town_id"], town["x"], town["y"]]
            viable_towns.append(town_data)
    
    # Sort the viable_towns list by the distance of each town to the player's location.
    viable_towns.sort(key=lambda town: distance_to(town[1:], player_data))
    
    # Iterate through the sorted list of towns and return the first town that has a level 5 hotel.
    for town in viable_towns:
        town_id = town[0]
        town_data = handler.post("building_hotel", "get_data", payload={"town_id": town_id}, action_name="mode")
        if int(town_data["hotel_level"]) == 5:
            return town
    
    # If no town with a level 5 hotel was found, return None.
    return None

def number_of_tasks(handler:requests_handler):
    """
    Returns the number of tasks in the queue.
    
    Args:
        handler: The API handler.
    
    Returns:
        The number of tasks in the queue.
    """
    # Make an API call to get the task queue data.
    response = handler.post("task", "")
    
    # Return the length of the queue.
    return len(response["queue"])
def sleep_task(handler:requests_handler, position_in_queue, city_id):
    """
    Adds a sleep task to the specified position in the queue.
    
    Args:
        handler: The API handler.
        position_in_queue: The position in the queue where the sleep task should be added.
        city_id: The ID of the city where the sleep task should be performed.
    
    Returns:
        The API response.
    """
    # Create a dictionary of parameters for the sleep task.
    payload = {
        f"tasks[{position_in_queue}][town_id]": f"{city_id}",
        f"tasks[{position_in_queue}][room]": f"luxurious_apartment",
        f"tasks[{position_in_queue}][taskType]": f"sleep"
    }
    
    # Make an API call to add the sleep task to the queue.
    return handler.post("task", "add", payload=payload, use_h=True)
def queue_sleep(handler:requests_handler, city_id):
    """
    Adds a sleep task to the end of the queue.
    
    Args:
        handler: The API handler.
        city_id: The ID of the city where the sleep task should be performed.
    
    Returns:
        The API response.
    """
    # Get the number of tasks in the queue.
    len_queue = number_of_tasks(handler)
    
    # Add a sleep task to the end of the queue.
    return sleep_task(handler, len_queue, city_id)
def sleep_closest_town(handler:requests_handler, player_data):
    """
    Adds a sleep task for the town with a level 5 hotel that is closest to the player's location.
    
    Args:
        handler: The API handler.
        player_data: The player's location and other relevant data.
    """
    # Find the town with a level 5 hotel that is closest to the player's location.
    town = get_closest_viable_town(handler, player_data)
    
    # Add a sleep task for the town to the end of the queue.
    queue_sleep(handler, town[0])