"""
This module contains functions related to parsing and analyzing data from the map in a game.

parse_map_data: Parses data retrieved from the server after requesting more data for the chuncks requested.
tiles_tw_gold: Divides the map into chunks based on the given number of chunks.
parse_map_tw_gold: Parses data from the complete map and returns a list of dictionaries containing gold and silver data.
"""

import math
import typing
import concurrent.futures
import itertools

import numpy as np

from the_west_inner.requests_handler import requests_handler


# Do not disturb , this function was written by someone else and I don't know how it works
# I parses the data retrieved from the server after requesting more data for the chuncks requested
def parse_map_data_for_gold_jobs(list_of_dynamic):
    list_munci =[]
    for index in range(len(list_of_dynamic)):
        for key in list_of_dynamic[index]:
            if type(list_of_dynamic[index][key]) is dict:
                for element in list_of_dynamic[index][key].items():
                    for x in element:
                        if type(x) is list:
                            for elements_of_list in x:
                                for another_dictionary in elements_of_list:
                                    if "gold" in another_dictionary:
                                        list_munci.append(another_dictionary)
    return list_munci
# Based on data retrieved from the minimap functions this function sectiones the map in n parts where n is the number of chuncks in the function argument
# Every single work location will be divided into tiles that are then separated into chunks
def tiles_map_search_by_key_word(handler:requests_handler,key_word:str,chuncks = 4)-> typing.List[list]:
    tiles= []
    TILE_SIZE = 256
    cautare_locatii_munci = handler.post(
                                window="map",
                                action="get_minimap",
                                action_name= "ajax").get(key_word)
    if cautare_locatii_munci == []:
        return []
    for each in cautare_locatii_munci.values():
        for coord_munci in each:
            x_tile = math.floor(coord_munci[0] / TILE_SIZE)
            y_tile = math.floor(coord_munci[1] / TILE_SIZE)
            if [x_tile,y_tile] not in tiles:
                tiles.append([x_tile,y_tile])
    tiles.sort()
    return [x.tolist() for x in np.array_split(tiles, chuncks)]
def parse_map_tw_gold(handler:requests_handler,num_chuncks:int = 4)-> typing.List[dict]:
    result = []
    args = tiles_map_search_by_key_word(handler = handler ,
                                        key_word= "job_groups",
                        chuncks = num_chuncks)
    for each in args:
        tile_request_payload = {"tiles":f"{each}"}
        tiles_data = handler.post(
                                window="map",
                                action="get_complete_data",
                                action_name= "ajax",
                                payload= tile_request_payload
        )
        result.append(tiles_data["dynamic"])
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.map(parse_map_data_for_gold_jobs, result)
    solution = list([item for sublist in future for item in sublist if item["silver"] == True])
    return solution

def parse_map_data_for_employers(nested_dict,employer_list = None):
    if employer_list is None:
        employer_list = []
    if isinstance(nested_dict,dict):
        if "employer" in nested_dict:
            return [nested_dict]
        if "x" in nested_dict:
            return []
        for value in nested_dict.values():
            employer_list = employer_list + parse_map_data_for_employers(nested_dict=value)
    if isinstance(nested_dict,list):
        for elem in nested_dict:
            employer_list = employer_list + parse_map_data_for_employers(nested_dict=elem)
    return employer_list

def parse_map_for_quest_employers(handler:requests_handler) -> typing.List[dict]:
    result = []
    
    map_raw_data =  tiles_map_search_by_key_word(handler = handler ,
                                        key_word= "quest_locations")
    
    for each in map_raw_data:
        tile_request_payload = {"tiles":f"{each}"}
        if each ==[]:
            continue
        tiles_data = handler.post(
                                window="map",
                                action="get_complete_data",
                                action_name= "ajax",
                                payload= tile_request_payload
        )
        result.append(tiles_data["quests"])
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.map(parse_map_data_for_employers, result)
    solution = itertools.chain.from_iterable(list(future))
    return list(solution)