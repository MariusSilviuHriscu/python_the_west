from dataclasses import dataclass
from requests_handler import requests_handler
from misc_scripts import number_of_tasks, distance_to
from player_data import Player_data
from work_list import Work_list


@dataclass
class Work:
    job_id : int
    x : int
    y : int
    duration : int
def work_task(handler:requests_handler,position_in_queue,work_object:Work,number_of_tasks=1):
    job_dict = {}
    for i in range(number_of_tasks):
        job_dict[f"tasks[{position_in_queue}][jobId]"] = f"{work_object.job_id}",
        job_dict[f"tasks[{position_in_queue}][x]"]= f"{work_object.x}",
        job_dict[f"tasks[{position_in_queue}][y]"]= f"{work_object.y}",
        job_dict[f"tasks[{position_in_queue}][duration]"] = f"{work_object.duration}",
        job_dict[f"tasks[{position_in_queue}][taskType]"]= "job"
    response = handler.post("task","add",payload=job_dict,use_h=True)
    return response
def queue_work(handler,work_object:Work):
    len_queue = number_of_tasks(handler)
    return work_task(handler,len_queue,work_object)





class munceste_coord():
    @staticmethod
    def secunde(id,handler):
        work_data = Work(id[0],id[1],id[2],15)
        return queue_work(handler,work_data)
    @staticmethod
    def minute(id,handler):
        work_data = Work(id[0],id[1],id[2],600)
        return queue_work(handler,work_data)
    @staticmethod
    def ore(id,handler):
        work_data = Work(id[0],id[1],id[2],3600)
        return queue_work(handler,work_data)
def get_work_locations(handler,job_id,job_list:Work_list):
    minimap = handler.post("map","get_minimap",action_name="ajax")
    job_group_dictionary = minimap["job_groups"]
    group_id = job_list.get_group_id(job_id)
    work_locations = job_group_dictionary[f"{group_id}"]
    return work_locations
def get_closest_workplace_data(handler,job_id,job_list:Work_list,player_data:Player_data):
    workplace_location_list = get_work_locations(handler,job_id,job_list)
    workplace_location_list.sort(key = lambda x:distance_to((x[0],x[1]),player_data))
    selected_work_coords = workplace_location_list[0]
    return (job_id,selected_work_coords[0],selected_work_coords[1])
