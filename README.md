# Python The West Bot

This project is a Python-based bot for the browser game "The West". It is designed to be used as a library to help you create your own automation scripts.

## Installation

To use this project, you'll need to have [Poetry](https://python-poetry.org/) installed.

1.  Clone the repository:

    ```bash
    git clone <repository-url>
    ```

2.  Navigate to the project directory:

    ```bash
    cd python_the_west
    ```

3.  Install the dependencies using Poetry:

    ```bash
    poetry install
    ```

4.  Activate the virtual environment created by Poetry:

    ```bash
    poetry shell
    ```


The project is divided into three main parts:

## `the_west_inner`

This is the core library for interacting with the game. It handles all the communication with the game server, manages the game state, and provides the tools to perform in-game actions.

## `automation_scripts`

Here you'll find a collection of scripts to automate various tasks, which you can use as a starting point for your own creations. This directory also includes powerful tools to help you build more complex automation, such as:

*   **A Concurrency Model:** This is built around a `CallbackChainer` class that allows you to schedule multiple functions (callbacks) to be executed during idle periods in your scripts. This provides a form of cooperative multitasking, allowing you to perform multiple actions concurrently. You have fine-grained control over how often each callback runs, using a set of flexible frequency rules (e.g., run every N seconds, run randomly, run only once, etc.).

*   **An Exception-Based Event Handler:** This is a system for controlling the flow of your scripts. It uses a decorator and a set of custom exceptions to allow you to pause, restart, or stop your scripts from anywhere in your code. This makes it easy to handle unexpected events and to manage complex script logic. For example, you can have a `CompleteStopEventException` that will gracefully stop the entire script, no matter how many nested functions you are in.

## `connection_sessions`

This package manages the connection to the game server. It's flexible and allows you to connect directly, through the Tor network, or using proxies.


## Usage

Here's a basic example of how to log in and get the main `Game_classes` object:

```python
from the_west_inner.login import Game_login
from the_west_inner.game_server import GameServer

# Instantiate the Game_login class with your credentials and world information
login = Game_login(
    player_name="your_username",
    player_password="your_password",
    world_id="your_world_id",
    server=GameServer.EN  # Example for the English server
)

# Call the login method to log in and get the Game_classes object
game_classes = login.login()
```

### The `Game_classes` Object

The `game_classes` object is the main object that holds all the game-related data and managers. It contains objects that are loaded at login and can only be obtained this way. It's your entry point to interact with the game. You can access all the different game components from this object, such as:

*   `handler`: The `requests_handler` object for making requests to the game server.
*   `player_data`: The `Player_data` object with information about your character.
*   `work_manager`: The `Work_manager` for starting jobs.
*   `consumable_handler`: The `Consumable_handler` for using items.
*   `equipment_manager`: The `Equipment_manager` for changing your equipment.
*   and many more...

### Basic Actions

After you have logged in and have the `game_classes` object, you can perform various actions.

**Printing current equipment:**
```python
# Print the current equipment
print(game_classes.equipment_manager.current_equipment)
```

**Changing equipment:**
```python
from the_west_inner.equipment import Equipment

# Create a new equipment set (replace with actual item IDs)
new_equipment = Equipment(
    head=123,
    neck=456,
    body=789,
    right_arm=101,
    left_arm=112,
    pants=131,
    shoes=415,
    animal=161
)

# Equip the new set
game_classes.equipment_manager.equip_equipment(
    equipment=new_equipment,
    handler=game_classes.handler
)
```

**Checking item count in bag:**
```python
# Check the number of a specific item in the bag (replace with actual item ID)
item_id_to_check = 12345
item_count = game_classes.bag[item_id_to_check]
print(f"You have {item_count} of item {item_id_to_check}.")
```

**Using a consumable:**
```python
# Use a consumable item (replace with actual item ID)
item_id_to_use = 67890
game_classes.consumable_handler.use_consumable(consumable_id=item_id_to_use)
```

### Using an Automation Script

Here's an example of how to use the `Cycle_jobs` automation script to work a list of jobs and use a `CallbackChainer` to print the player's health every 30 seconds.

```python
from the_west_inner.work import Work
from the_west_inner.player_data import Player_data
from the_west_inner.requests_handler import requests_handler
from automation_scripts.work_cycle import Cycle_jobs
from automation_scripts.sleep_func_callbacks.callback_chain import CallbackChainer
from automation_scripts.sleep_func_callbacks.callback_frequency import EveryNSeconds
from automation_scripts.sleep_func_callbacks.universal_callback_map import UNIVERSAL_MAPPING

# First, log in and get the game_classes object as shown above

# Define a list of jobs to perform
job_list = [
    Work(job_id=1, x=123, y=456, duration=15),
    Work(job_id=2, x=789, y=101, duration=15)
]

# Create a CallbackChainer and provide it with the game_classes object
# This allows the chainer to automatically inject game objects into your callbacks
callback_chainer = CallbackChainer(type_map_list=UNIVERSAL_MAPPING)
callback_chainer.add_default_kwargs(game_classes=game_classes)

# Define a callback function that prints the player's health
# The Player_data and requests_handler objects are automatically injected by the CallbackChainer
def print_player_health(player_data: Player_data, handler: requests_handler):
    player_data.update_all(handler=handler) # Make sure we have the latest data
    print(f"Player health: {player_data.hp}")

# Add the callback to the chainer with a frequency rule
callback_chainer.add_callback(print_player_health)
callback_chainer.set_frequency(EveryNSeconds(time_seconds=30))


# Instantiate the Cycle_jobs class
work_cycle = Cycle_jobs(
    game_classes=game_classes,
    job_data=job_list,
    consumable_handler=game_classes.consumable_handler
)

# Set the callback chainer for the work cycle
work_cycle.update_work_callback_chainer(callback_chain=callback_chainer)

# Start the work cycle
work_cycle.cycle(
    motivation_consumable=12345,  # Replace with the actual item ID
    energy_consumable=67890,      # Replace with the actual item ID
    number_of_cycles=5
)
```

### Using the Event Handler

Here's a simple example of how to use the `handle_exceptions` decorator and the `StopEvent` to gracefully stop a script and execute a callback.

```python
from automation_scripts.stop_events.script_events import StopEvent
from automation_scripts.stop_events.script_exception_handler import handle_exceptions

def cleanup_function():
    print("Script is stopping, performing cleanup...")

def some_nested_function():
    print("Something went wrong, stopping the script...")
    StopEvent(callback_func=cleanup_function).raise_exception()

def some_other_function():
    print("Doing some work...")
    some_nested_function()
    print("This will not be printed.")

@handle_exceptions
def main_script():
    print("Starting the main script...")
    some_other_function()
    print("This will also not be printed.")

# Start the script
main_script()

print("Script has been stopped.")
```

Here's a more practical example that demonstrates both `StopEvent` and `CompleteStopEvent` in a duel script.

```python
from automation_scripts.stop_events.script_events import StopEvent, CompleteStopEvent
from automation_scripts.stop_events.script_exception_handler import handle_exceptions
from the_west_inner.player_data import Player_data
from the_west_inner.consumable import Consumable_handler
from the_west_inner.bag import Bag

def heal_player(consumable_handler: Consumable_handler):
    print("Player health is low, healing...")
    # Replace with the actual item ID for a healing item
    consumable_handler.use_consumable(consumable_id=12345)

def check_health(player_data: Player_data, consumable_handler: Consumable_handler, bag: Bag):
    player_data.update_all(handler=game_classes.handler) # Make sure we have the latest data
    if player_data.hp < 500:
        healing_item_id = 12345 # Replace with the actual item ID
        if healing_item_id in bag:
            print("Health is critical, stopping duels to heal.")
            StopEvent(callback_func=heal_player, consumable_handler=consumable_handler).raise_exception()
        else:
            print("Health is critical and no healing items are available. Stopping the script.")
            CompleteStopEvent().raise_exception()

@handle_exceptions
def duel_script(player_data: Player_data, consumable_handler: Consumable_handler, bag: Bag):
    print("Starting the duel script...")
    for i in range(10):
        print(f"Starting duel #{i+1}")
        # In a real script, you would perform a duel here
        # For this example, we'll just simulate losing health
        player_data.hp -= 100
        check_health(player_data=player_data, consumable_handler=consumable_handler, bag=bag)
        print("Duel finished.")
    print("Duel script finished successfully.")

# First, log in and get the game_classes object as shown above
# Then, you can run the duel_script
duel_script(
    player_data=game_classes.player_data,
    consumable_handler=game_classes.consumable_handler,
    bag=game_classes.bag
)

print("Script has been stopped.")
```
