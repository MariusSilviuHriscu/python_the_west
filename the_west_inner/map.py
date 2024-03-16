"""
This module contains classes and functions for creating and manipulating map objects for a game.

Classes:

    Map_job_location: Represents a single job on the map, with attributes for job group ID, job ID, coordinates, and a boolean indicating if it is a "silver" job.
    Map_county: Represents a county on the map, with attributes for coordinates, name, ID, and lists of neighboring counties and job groups within the county.
    Map: Contains a list of Map_county objects and a method for finding the Map_county object for a given set of coordinates.

Functions:

    create_job_group_jobs_dict: Takes a Work_list object and returns a dictionary with job group IDs as keys and lists of job IDs as values.
    create_map_job_location_list: Takes a Work_list object and a dictionary of job group locations, and returns a list of Map_job_location objects.
"""
import random
import typing
from requests_handler import requests_handler
from work_list import Work_list
from towns import Town_list,Town
from player_data import Player_data
from gold_finder import parse_map_tw_gold

class Map_job_location():
    def __init__(self,job_group_id:int,job_id:int,job_x:int,job_y:int,is_silver:bool) -> None:
        self.job_group_id = job_group_id
        self.job_id = job_id
        self.job_x = job_x
        self.job_y = job_y
        self.is_silver = is_silver
    def job_is_silver(self)-> bool:
        return self.is_silver
    def set_to_silver(self)-> None:
        self.is_silver = True
    def __str__(self) -> str:
        return f"job_group_id:{self.job_group_id},job_id:{self.job_id},job_x:{self.job_x},job_y:{self.job_y},is_silver:{self.is_silver}"
    def __repr__(self) -> str:
        return f"job_group_id:{self.job_group_id},job_id:{self.job_id},job_x:{self.job_x},job_y:{self.job_y},is_silver:{self.is_silver}"

    def __hash__(self) -> int:
        
        return hash(
            (self.job_id,
             self.job_x,
             self.job_y)
        )

MapJobLocationDictType = dict[
    tuple[int,int,int] | Map_job_location , Map_job_location   
]

class MapJobLocationData:
    def __init__(self , map_job_location_list : list[Map_job_location]):
        
        self.map_job_location_dict : MapJobLocationDictType  = {x : x for x in map_job_location_list}
        
        self._loaded_silver_jobs = any([x.is_silver for x in map_job_location_list])
    
    def complete_silver_jobs(self, handler: requests_handler ) -> None:
        
        silver_jobs = parse_map_tw_gold(handler = handler)
        
        for silver_job in silver_jobs:
            
            if not silver_job.get('silver'):
                continue
            id_location_tuple = (
                silver_job['job_id'],
                silver_job['x'],
                silver_job['y']
            )
            
            job = self.map_job_location_dict.get(id_location_tuple , None)
            
            if job is None:
                raise ValueError("Silver job loaction couldn't be found !")
            
            job.set_to_silver()
        
        self._loaded_silver_jobs = True
    
    @property
    def loaded_silver_job(self) -> bool:
        return self._loaded_silver_jobs
                    
        
    def get_closest_job(self ,job_id : id , player_data : Player_data) -> Map_job_location:
        
        minimum_job = None
        min_distance = None
        
        job_list = [x for x in self.map_job_location_dict.values() if x.job_id == job_id]
        
        for job in job_list :
            
            distance = player_data.absolute_distance_to(final_position= (job.job_x, job.y)
                                                        )
            
            if min_distance is None or distance < min_distance :
                
                min_distance = distance
                minimum_job = job
        
        return minimum_job
    
    def get_random_job(self,job_id : int) -> Map_job_location:
        
        return random.choice(
            [x for x in self.map_job_location_dict.values() if x.job_id == job_id]
        )

def create_job_group_jobs_dict(work_list:Work_list)-> dict:
    '''
    This looks at all the jobs in the work list and creates a dictionary where the key is the job_group_id and the value is a list of all the jobs in that group
    '''
    job_group_dict = {}
    for job,job_data in work_list.work_dict.items():
        if job_data["groupid"] not in job_group_dict:
            job_group_dict[job_data["groupid"]] = [job]
        else:
            job_group_dict[job_data["groupid"]].append(job)
    return job_group_dict
def create_map_job_location_list(work_list:Work_list,job_group_locations:dict)-> typing.List[Map_job_location]:
    '''
    This creates a list of Map_job_location objects that are used to create the map.
    It calls the create_job_group_jobs_dict function to create a dictionary of job_group_ids and their corresponding jobs and then combines that with the job_group_locations dictionary to create the list of Map_job_location objects
    '''
    job_locations_map = []
    job_group_dict = create_job_group_jobs_dict(work_list)
    for job_group_id,job_list in job_group_dict.items():
        for job in job_list:
            job_locations_map += [Map_job_location(job_group_id=job_group_id,
                                                    job_id=job,
                                                    job_x=job_location[0],
                                                    job_y=job_location[1],
                                                    is_silver=False) for job_location in job_group_locations[f'{job_group_id}']]
    return job_locations_map

class Map_county():
    '''This is the reprezentation of a map county.
    It contains the map coordinates , it's neighbours and it's component job groups
    '''
    def __init__(self,start_x:int,start_y:int,end_x:int,end_y:int,name:str,county_id:int) -> None:
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.name = name
        self.county_id = county_id
        self.neighbours = []
        self.county_job_groups = dict()
    def add_job_group(self,job_group_id:int,job_group_coords:typing.List[int]) -> None:
        if job_group_id in self.county_job_groups : 
            self.county_job_groups[job_group_id].append(job_group_coords)
        else :
            self.county_job_groups[job_group_id] = [job_group_coords]
    def add_neighbour(self,county_id:int) -> None:
        self.neighbours.append(county_id)
    def countains(self,x:int,y:int) -> bool:
        if self.start_x <= x <= self.end_x and self.start_y <= y <= self.end_y:
            return True
        return False
class Map_county_list():
    def __init__(self,counties:typing.List[Map_county]) -> None:
        self.counties = counties
    def are_counties_neighbors(self, county1: Map_county, county2: Map_county) -> bool:
        return (
            county1.start_x <= county2.end_x
            and county1.end_x >= county2.start_x
            and county1.start_y <= county2.end_y
            and county1.end_y >= county2.start_y
        )
    
    # method that establishes the neighbours of each county based on the start and end coords
    # a county is a neighbour of another county if it has at least one point in common with it
    # counties are not of the same size but they are all rectangles
    
    def create_neighbours(self) -> None:
        for county in self.counties:
            county.neighbours = []
        for county in self.counties :
            edges = [[county.start_x,county.start_y],[county.end_x,county.start_y],[county.start_x,county.end_y],[county.end_x,county.end_y]]
            for edge in edges:
                neighbours = filter (
                        lambda x :x.start_x-1 <= edge[0]<=x.end_x+1 and x.start_y-1 <= edge[1] <= x.end_y+1 if x.county_id not in county.neighbours else False,
                        self.counties
                        )
                for neighbour in neighbours:
                    if neighbour not in neighbour.neighbours and neighbour.county_id != county.county_id:
                        county.add_neighbour(neighbour.county_id)
    def create_neighbours(self) -> None:
        for county1 in self.counties:
            for county2 in self.counties:
                if county1.county_id != county2.county_id and self.are_counties_neighbors(county1, county2):
                    county1.add_neighbour(county2.county_id)
    def __getitem__(self,county_id:int)-> Map_county:
        for county in self.counties:
            if county.county_id == county_id:
                return county
        raise Exception("County does not exist")    
    # make this class iterable
    def __iter__(self):
        for offer in self.counties:
            yield offer
    def __next__(self):
        return self.counties.__next__()
def assemble_map_county_list_from_request_data(county_data:dict) -> Map_county_list:
    return Map_county_list( [Map_county(
                    start_x = county['start_x'],
                    start_y = county['start_y'],
                    end_x = county['end_x'],
                    end_y = county['end_y'],
                    name = county['name'],
                    county_id = county['county_id']
                    ) for county in county_data] 
                           )
def assemble_map_town_list_from_request_data(town_dict:dict) -> Town_list:
    town_list = {town["town_id"] : Town( x = town["x"],
                                                y = town["y"],
                                                town_id = town["town_id"],
                                                town_name= town["name"],
                                                member_count = town["member_count"],
                                                npctown = town["npctown"],
                                                town_points = town["town_points"],
                                                alliance_id = town["alliance_id"]) 
                            for town in town_dict.values()}
    return Town_list(town_list=town_list)
    
class Map():
    def __init__(self ,
                 minimap_data : dict,
                 towns : Town_list,
                 counties : Map_county_list,
                 fair : dict ,
                 job_location_data : MapJobLocationData):
        
        self.minimap_data = minimap_data
        self.towns = towns
        self.counties = counties
        self.fair = fair
        self.job_location_data = job_location_data

class MapLoader:
    
    def __init__(self ,
                 handler: requests_handler ,
                 player_data : Player_data ,
                 work_list : Work_list):
        self.handler = handler
        self.player_data = player_data
        self.work_list = work_list
        
    def _init_map(self) -> dict:
        response = self.handler.post(window = "map",
                                     action_name="ajax",
                                     action = "get_minimap")
        if response['error'] == True :
            raise Exception("Invalid minimap response")
        return response
    
    def _build_towns(self, minimap : dict) -> Town_list:
        
        return assemble_map_town_list_from_request_data(town_dict= minimap['towns'])
    
    def _build_counties(self, minimap : dict) -> Map_county_list:
        
        return assemble_map_county_list_from_request_data(minimap['counties'])
    
    def _build_fairs(self, minimap : dict) -> dict:
    
        return minimap['fair']
    def _build_job_groups(self,minimap : dict) -> dict:
        
        return minimap['job_groups']
    
    def _build_map_job_location_list(self,minimap : dict) -> list[Map_job_location]:
        
        
        
        return create_map_job_location_list(
            work_list = self.work_list,
            job_group_locations = self._build_job_groups(minimap = minimap)
        )
    
    def _build_map_job_location_data(self , minimap : dict , load_silver_jobs : bool) -> MapJobLocationData:
        
        map_job_location_data = MapJobLocationData(
            map_job_location_list = self._build_map_job_location_list(minimap = minimap )
        )
        
        if load_silver_jobs :
            map_job_location_data.complete_silver_jobs(handler=self.handler)
        
        return map_job_location_data
    
    def build(self, load_silver_jobs : bool = False) -> Map:
        
        minimap_data = self._init_map()
        towns = self._build_towns(minimap = minimap_data)
        counties = self._build_counties(minimap = minimap_data)
        fairs = self._build_fairs(minimap = minimap_data)
        job_groups = self._build_map_job_location_data(minimap = minimap_data , load_silver_jobs = load_silver_jobs)
        
        return Map(
            minimap_data = minimap_data,
            towns = towns,
            counties = counties,
            fair = fairs,
            job_location_data=job_groups
        )
        