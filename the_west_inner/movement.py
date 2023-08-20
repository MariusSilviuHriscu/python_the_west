"""
This module handles character movement in a game, including calculating the distance and travel time between two locations.

Classes:
- character_movement: A class for calculating the distance and travel time between two locations for a character in a game.

Functions:
- distance(initial_position, final_position) -> float: Calculates the Euclidean distance between two locations.
- calc_distanta(initial_position, final_position) -> int: Calculates the time it would take for a character to travel between two locations.
- cal_distanta_catre(final_position) -> int: Calculates the time it would take for a character to travel from its current position to a specified final position.

Dataclass:
- Game_data: Stores game data such as the travel speed.
"""

from dataclasses import dataclass
import math


class character_movement:
    """
    A class for calculating the distance and travel time between two locations for a character in a game.
    """
    
    def __init__(self, x, y, game_travel_speed, character_speed):
        """
        Initializes the class with the character's starting position, the game's travel speed,
        and the character's speed.
        
        Args:
            x: The x coordinate of the character's starting position.
            y: The y coordinate of the character's starting position.
            game_travel_speed: The game's travel speed, which affects the time it takes for a character to travel.
            character_speed: The character's speed, which affects the time it takes for the character to travel.
        """
        # Store the character's starting position and movement coefficients.
        self.character_position = (x, y)
        self.movement_coefficient = game_travel_speed * character_speed
    
    def distance(self, initial_position, final_position):
        """
        Calculates the Euclidean distance between two locations.
        
        Args:
            initial_position: The initial position (x, y coordinates).
            final_position: The final position (x, y coordinates).
        
        Returns:
            The Euclidean distance between the two positions.
        """
        # Calculate the Euclidean distance between the two positions.
        return math.sqrt((initial_position[0] - final_position[0]) * (initial_position[0] - final_position[0]) + (initial_position[1] - final_position[1]) * (initial_position[1] - final_position[1]))
    def calc_distanta(self, initial_position, final_position):
        """
        Calculates the time it would take for a character to travel between two locations.
        
        Args:
            initial_position: The initial position (x, y coordinates).
            final_position: The final position (x, y coordinates).
        
        Returns:
            The time it would take for a character to travel between the two positions.
        """
        # Calculate the time it would take for a character to travel between the two positions.
        return math.ceil(self.distance(initial_position, final_position) * self.movement_coefficient)
    def cal_distanta_catre(self, final_position):
        """
        Calculates the time it would take for a character to travel from its current position to a specified final position.
        
        Args:
            final_position: The final position (x, y coordinates).
        
        Returns:
            The time it would take for a character to travel from its current position to the final position.
        """
        # Calculate the time it would take for a character to travel from its current position to the final position.
        return self.calc_distanta(self.character_position, final_position)

@dataclass
class Game_data:
    game_travel_speed:float
