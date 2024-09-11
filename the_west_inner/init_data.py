import typing
from bs4 import BeautifulSoup
import time
import datetime
import json
import re

"""
This module contains functions for parsing information from the game's initialization HTML.

Functions:

return_h: Extracts the h value from the initialization HTML.h (str): A value used in requests_handler for making requests.
return_work_list: Extracts the list of available jobs from the initialization HTML.
return_bag: Extracts the list of items in the player's bag from the initialization HTML.
return_cooldown: Extracts the date of the next cooldown period from the initialization HTML.
return_premium_data: Extracts premium bonus data from the initialization HTML.
return_wear_data : Extracts equipment data from the initialization HTML
"""

CORRESPONDING_EVENT_WOF = {
    'Independence' : 'independencewof',
    'fairwof' : 'fairwof'
}


def return_h(login_data):
    soup = BeautifulSoup(login_data.text, 'html.parser')
    return soup.find("body").find("script").contents[0].split("""Player.init({"h":""")[1].split(",")[0].replace("\"","")
def return_work_list(initialization_html):
    jsonStr_list = re.findall(r'\{.*\}', str(initialization_html))
    json_item = json.loads(jsonStr_list[2])
    return json_item["jobs"]
def return_bag(initialization_html):
    jsonStr_list = re.findall(r'\{.*\}', str(initialization_html))
    json_item = json.loads(jsonStr_list[4])
    bag_dict = json_item["bag"]
    returnable= []
    for item_type in bag_dict:
        for item in bag_dict[item_type]:
            returnable.append(item)
    return returnable
def return_cooldown_when_everything_fails(initialization_html:str)->datetime.datetime:
    jsonStr_list = re.findall(r'\{.*\}', str(initialization_html))
    json_item = json.loads(jsonStr_list[16])
    raw_time_data = json_item["itemuseCooldown"]
    game_time = time.ctime(float(raw_time_data))
    game_time = datetime.datetime.strptime(game_time,"%c")
    return game_time

def return_cooldown(initialization_html:str)->datetime.datetime:
    jsonStr_list = re.findall(r'\{.*\}', str(initialization_html))
    for string_found in jsonStr_list:
        if "itemuseCooldown" in string_found:
            json_item = json.loads(string_found)
            raw_time_data = json_item["itemuseCooldown"]
            game_time = time.ctime(float(raw_time_data))
            game_time = datetime.datetime.strptime(game_time,"%c")
            return game_time
    return return_cooldown_when_everything_fails(initialization_html=initialization_html)
def return_premium_data(initialization_html):
    jsonStr_list = re.findall(r'\{.*\}', str(initialization_html))
    json_item = json.loads(jsonStr_list[5])
    return json_item["premiumBoni"]
def return_wear_data(initialization_html):
    jsonStr_list = re.findall(r'\{.*\}', str(initialization_html))
    for string_found in jsonStr_list:
        if "wear" in jsonStr_list:
            json_item = json.loads(string_found)
            raw_time_data = json_item["wear"]
            game_time = time.ctime(float(raw_time_data))
            game_time = datetime.datetime.strptime(game_time,"%c")
            return game_time
def return_wear_data(initialization_html):
    jsonStr_list = re.findall(r'\{.*\}', str(initialization_html))
    json_item = json.loads(jsonStr_list[4])
    wear_list = json_item["wear"]
    return wear_list
def return_buff_data(initialization_html):
    jsonStr_list = re.findall(r'\{.*\}', str(initialization_html))
    target_string ="{'buffs':[]}"
    for string_found in jsonStr_list:
        if 'buffs' in string_found:
            target_string = string_found
    json_item = json.loads(target_string)
    
    return json_item['buffs']
def return_currency_data(initialization_html:str)->dict[str,int]:
    search_dict = ['cash','deposit','upb','nuggets','veteranPoints']
    jsonStr_list = re.findall(r'\{.*\}', str(initialization_html))
    for string_found in jsonStr_list:
        if "cash" in string_found:
            json_player_data = json.loads(string_found)
            return {key : json_player_data.get(key) for key in search_dict}


def return_current_fair_data(initialization_html : str) -> dict[str , str | int ]:
    
    jsonStr_list = re.findall(r'\{.*\}', str(initialization_html))
    for json_item in jsonStr_list:
        
        try:
            
            dict_data = json.loads(json_item)
            
            if dict_data.get('type', None) == 'fairwof' :
                
                return dict_data
        
        except :
            pass
    return {}
                

def return_current_event_data(initialization_html : str) -> dict[str,str|int] | list[typing.Never]:
    
    jsonStr_list = re.findall(r'\{.*\}', str(initialization_html))
    json_item = json.loads(jsonStr_list[2])
    
    return json_item["sesData"]


def get_wof_id_by_event_name(initialization_html : str , event_name : str) -> dict[str,str|int]:
    
    jsonStr_list = re.findall(r'\{.*\}', str(initialization_html))
    wof_type = CORRESPONDING_EVENT_WOF.get(event_name, None)
    for json_item in jsonStr_list:

        try :
            
                
            dict_data = json.loads(json_item)

            if wof_type and dict_data.get('type', None) == wof_type:
                return dict_data.get('id')
        except Exception as e:
            pass
        
        if json_item.startswith('{') and json_item.endswith('}'):
            try :
            
                    
                dict_data = json.loads(f'[{json_item}]')
                for event in dict_data:
                    if wof_type and event.get('type', None) == wof_type:
                        return event.get('id')
            except Exception as e:
                pass