from dataclasses import dataclass

from requests_handler import requests_handler
from player_data import Player_data
from work_manager import Work_manager
from town_buildings import Town_buildings,load_town_buildings
@dataclass
class Town():
    x : int
    y : int
    town_id : int
    town_name : str
    member_count : int
    npctown : bool
    town_points : int 
    alliance_id : int 
    def inner_data(self,handler:requests_handler,work_manager:Work_manager,player_data : Player_data) -> Town_buildings:
        return load_town_buildings(
                                    handler= handler,
                                    work_manager = work_manager,
                                    player_data = player_data,
                                    coords= (self.x,self.y)
                                    )

class Town_list():
    def __init__(self,town_data:dict):
        self.town_list = {town["town_id"] : Town( x = town["x"],
                                                y = town["y"],
                                                town_id = town["town_id"],
                                                town_name= town["name"],
                                                member_count = town["member_count"],
                                                npctown = town["npctown"],
                                                town_points = town["town_points"],
                                                alliance_id = town["alliance_id"]) 
                            for town in town_data.values()}
    def __getitem__(self,key):
        return self.town_list[key]
    def return_populated_towns(self) -> list[Town]:
        return [town for town in self.town_list.values() if town.member_count > 0]
    def get_closest_town(self, player_data : Player_data) -> Town:
        """
        Get the closest populated town to the player.

        Args:
            player_data (Player_data): Player data instance.

        Returns:
            Town: The closest populated town to the player.
        """
        populated_towns = [town for town in self.town_list.values() if town.member_count > 0]

        if not populated_towns:
            # No populated towns available
            return None
        # Calculate distances to all populated towns
        distances = {
            town: player_data.absolute_distance_to((town.x, town.y))
            for town in populated_towns
        }

        # Find the town with the minimum distance
        closest_town = min(distances, key=distances.get)

        return closest_town
