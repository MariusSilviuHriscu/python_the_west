from dataclasses import dataclass
import typing

from requests_handler import requests_handler
from player_data import Player_data
from work_manager import Work_manager
from town_buildings import Town_buildings,load_town_buildings,CityNotFoundError

@dataclass
class TownBuildingLevelMap:
    town_id : int
    building_name : str
    level : int
    max_level : int
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
    def __hash__(self) -> int:
        return hash(self.town_id)
    def inner_data(self,handler:requests_handler,work_manager:Work_manager,player_data : Player_data) -> Town_buildings:
        return load_town_buildings(
                                    handler= handler,
                                    work_manager = work_manager,
                                    player_data = player_data,
                                    coords= (self.x,self.y)
                                    )
    def town_level_map_data(self,handler:requests_handler,city_building_name : str) -> TownBuildingLevelMap:
        
        response = handler.post(window="town",action="get_town",action_name="mode",payload={"x":f"{self.x}","y":f"{self.y}"})
    
        if response['error'] :
            raise CityNotFoundError(f"Couldn't find the city at the coords ( {self.x} , {self.y} ) !")
    
    
        building_data = response.get('allBuildings').get(city_building_name)
        
        return TownBuildingLevelMap(
            town_id= self.town_id,
            building_name = city_building_name,
            level = building_data.get('stage'),
            max_level = building_data.get('maxStage')
        )

        
class Town_list():
    def __init__(self,town_list : dict[int,Town]):
        self.town_list = town_list
    def __getitem__(self,key ):
        return self.town_list[key]
    def __iter__(self):
        return self.town_list.values().__iter__()
    def return_populated_towns(self) -> typing.Self:
        return Town_list(
                        town_list = {town_id:town for town_id,town in self.town_list.items() if town.member_count > 0}
                        )
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
