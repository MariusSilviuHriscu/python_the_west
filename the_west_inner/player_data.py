"""
This module handles player data and related functions in a game, including updating player location, character movement speed, character variables, and profession.

Class:
- Player_data: A class representing the data for a player in a game.
Methods:
    - update_visible_variables(handler: requests_handler) -> None: Updates the player's location (x and y coordinates) and profession based on the player's ID and name.
    - update_character_movement(handler: requests_handler) -> None: Updates the character's movement speed.
    - update_character_variables(handler: requests_handler) -> None: Updates the character's hit points, energy, level, and experience.
    - update_crafting(handler: requests_handler) -> None: Updates the character's profession based on the player's ID and name.
    - update_all(handler: requests_handler) -> None: Calls all the update methods to update the player's location, character movement speed, character variables, and profession.
    - absolute_distance_to(final_position: typing.Tuple[int, int]) -> float: Calculates the absolute distance between the player's current position and a final position.
    - time_to_travel(final_position: typing.Tuple[int, int]) -> int: Calculates the time it would take for the player to travel from their current position to a final position.
    - time_to_travel_and_back(final_position: typing.Tuple[int, int]) -> int: Calculates the time it would take for the player to travel to a location and back.
"""

from dataclasses import dataclass
import typing
import time
from enum import Enum, auto

from requests_handler import requests_handler
from movement import character_movement,Game_data


class ClassTypeEnum(Enum):
    GREENHORN = auto()
    ADVENTURER = auto()
    DUELIST = auto()
    SOLDIER = auto()
    WORKER = auto()

@dataclass
class ExpData:
    experience : int
    curent_level_exp : int
    level_exp_requirement : int
    
    def required_exp(self) -> int:
        return self.level_exp_requirement - self.curent_level_exp
@dataclass
class Player_data:
    """
    A class representing the data for a player in a game.
    """
    id: int
    x: int
    y: int
    name: str
    game_data: Game_data
    character_movement: float
    hp: int
    hp_max: int
    energy: int
    energy_max: int
    level: int
    experience: int
    exp_data : ExpData
    class_name : str
    class_key : str
    profession_id: int = -1
    profession: str = "None"
    town_id : int|None = None
    
    def update_visible_variables(self, handler: requests_handler):
        """
        Updates the player's location (x and y coordinates) and profession based on the player's ID and name.
        Also updates the player's town_id
        
        Args:
            handler: An instance of the requests_handler class used to make requests to the game API.
        """
        profile_search_response = handler.post("profile", "init", payload={"playerId": f"{self.id}", "name": f"{self.name}"}, use_h=False, action_name="mode")
        self.x = profile_search_response["x"]
        self.y = profile_search_response["y"]
        
        self.class_name = profile_search_response['className']
        self.class_key = profile_search_response['classKey']
        
        if profile_search_response["profession"] is not None:
            self.profession_id = profile_search_response["profession"]["id"]
            self.profession = profile_search_response["profession"]["name"]
        else :
            self.profession_id = -1
            self.profession = ""
        self.town_id = None
        if profile_search_response['hasTown']:
            self.town_id = profile_search_response['town']
        time.sleep(0.5)
    def update_character_movement(self, handler: requests_handler):
        """
        Updates the character's movement speed.
        
        Args:
            handler: An instance of the requests_handler class used to make requests to the game API.
        """
        response = handler.post("character", "ajax_get_buffs", action_name="mode")
        self.character_movement = response['speed']
        time.sleep(0.5)
    
    def update_character_variables(self, handler: requests_handler):
        """
        Updates the character's hit points, energy, level, and experience.
        
        Args:
            handler: An instance of the requests_handler class used to make requests to the game API.
        """
        response = handler.post("character","","")
        self.hp = response["healthCurrent"]
        self.hp_max = response["healthMax"]
        self.energy = response["energyCurrent"]
        self.energy_max = response["energyMax"]
        self.level = response["level"]
        self.experience = response["exp"]

        exp_current_level = response['expThis']
        exp_next_level = response['expNext']
        
        self.exp_data = ExpData(
            experience = self.experience,
            curent_level_exp = self.experience - exp_current_level,
            level_exp_requirement = exp_next_level - exp_current_level
        )
        
    def update_crafting(self, handler: requests_handler):
        """
        Updates the character's profession based on the player's ID and name.
        
        Args:
            handler: An instance of the requests_handler class used to make requests to the game API.
        """
        profile_search_response = handler.post("profile", "init", payload={"playerId": f"{id}", "name": f"{self.name}"}, use_h=False, action_name="mode")
        
        if profile_search_response["profession"] is not None:
            self.profession_id = profile_search_response["profession"]["id"]
            self.profession = profile_search_response["profession"]["name"]
    
    def update_all(self, handler: requests_handler):
        """
        Calls all the update methods to update the player's location, character movement speed,
        character variables, and profession.
        
        Args:
            handler: An instance of the requests_handler class used to make requests to the game API.
        """
        self.update_character_movement(handler)
        self.update_character_variables(handler)
        self.update_visible_variables(handler)
        self.update_crafting(handler)
    
    def absolute_distance_to(self, final_position: typing.Tuple[int, int]) -> int:
        """
        Calculates the absolute distance between the player's current position and a final position.
        
        Args:
            final_position: The final position (x, y coordinates) to which the distance should be calculated.
        
        Returns:
            The absolute distance between the player's current position and the final position.
        """
        return character_movement(self.x, self.y, self.game_data.game_travel_speed, self.character_movement).calculate_distance_to(final_position)
    
    def update_hp(self, value: int):
        """
        Updates the character's hit points.
        
        Args:
            value: The new value for the character's hit points.
        """
        self.hp = value
    
    def update_energy(self, value: int):
        """
        Updates the character's energy.
        
        Args:
            value: The new value for the character's energy.
        """
        self.energy = value
    @property
    def required_exp(self) -> int:
        
        return self.exp_data.required_exp()
    
    def select_class(self, handler: requests_handler , class_type_enum : ClassTypeEnum):
        
        if self.level < 15 :
            raise ValueError(f'Cannot select class before level 15 now you have : {self.level}')
        if self.class_key != 'greenhorn':
            raise Exception(f'You already  have a class selected !')
        
        payload = {'charclass' : str(class_type_enum)}
        
        response = handler.post(
            window = 'class_choose',
            action = 'choose',
            payload = payload ,
            use_h = True
        )
        
        if response.get('error' , False):
            raise Exception('Something went wrong with choosing class')
        
        self.update_all(handler = handler)
    