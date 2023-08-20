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

import typing
from requests_handler import requests_handler
from work_list import Work_list
from towns import Town_list

class Map_job_location():
    def __init__(self,job_group_id:int,job_id:int,job_x:int,job_y:int,is_silver:bool) -> None:
        self.job_group_id = job_group_id
        self.job_id = job_id
        self.job_x = job_x
        self.job_y = job_y
        self.is_silver = is_silver
    def is_silver(self)-> bool:
        return self.is_silver
    def set_to_silver(self)-> None:
        self.is_silver = True
    def __str__(self) -> str:
        return f"job_group_id:{self.job_group_id},job_id:{self.job_id},job_x:{self.job_x},job_y:{self.job_y},is_silver:{self.is_silver}"
    def __repr__(self) -> str:
        return f"job_group_id:{self.job_group_id},job_id:{self.job_id},job_x:{self.job_x},job_y:{self.job_y},is_silver:{self.is_silver}"
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
class Map():
    def __init__(self,handler : requests_handler):
        self.handler = handler
        minimap = self._init_map()
        self.towns = minimap['towns']
        self.towns = Town_list(town_data= minimap['towns'])
        self.counties = assemble_map_county_list_from_request_data(minimap['counties'])
        self.fair = minimap['fair']
        self.job_groups = minimap['job_groups']
    def _init_map(self) -> dict:
        response = self.handler.post(window = "map",
                                     action_name="ajax",
                                     action = "get_minimap")
        if response['error'] == True :
            raise Exception("Invalid minimap response")
        return response