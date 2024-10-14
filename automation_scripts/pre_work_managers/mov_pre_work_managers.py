

import copy
from the_west_inner import requests_handler
from the_west_inner.equipment import Equipment, Equipment_manager
from the_west_inner.game_classes import Game_classes
from the_west_inner.movement_manager import MovementManager
from the_west_inner.towns import Town
from the_west_inner.work import Work
from the_west_inner.work_list import Work_list
from the_west_inner.work_manager import Work_manager



WorkIdType = int
XCoord = int
YCoord = int
WorkMovementTableType = dict[
    tuple[WorkIdType,XCoord,YCoord] , int | Work | Town
]

class PreWorkMovementManager:
    
    def __init__(self , 
                 work_table : WorkMovementTableType,
                 work_manager : Work_manager ,
                 movement_equipment : Equipment ,
                 equipment_manager : Equipment_manager,
                 movement_manager : MovementManager):
        
        self.work_table = work_table
        
        self.equipment_manager = equipment_manager
        self.work_manager = work_manager
        self.movement_equipment = movement_equipment
        self.movement_manager = movement_manager
    
    def _move_to_entity(self ,base_work: Work ,  move_obj : int | Work | Town):
        
        if isinstance(move_obj , int):
            
            return self.movement_manager.move_to_job(
                job_id = move_obj,
                x = base_work.x,
                y = base_work.y
            )
        elif isinstance(move_obj , Work):
            return self.movement_manager.move_to_job(
                job_id = move_obj.job_id,
                x = move_obj.x,
                y = move_obj.y
            )
        elif isinstance(move_obj , Town):
            return self.movement_manager.move_to_town(
                town = move_obj
            )
        
        raise Exception(f'Could not move to desired object {type(move_obj)}')
        
        
    def handle_movement(self , work : Work , handler : requests_handler):
        work_tuple : tuple[WorkIdType,XCoord,YCoord] = (work.job_id,work.x,work.y)
        if work_tuple not in self.work_table:
            
            raise ValueError(f'No value for work id :{work.job_id} !')
        
        self.work_manager.wait_until_free_queue()
        
        work_movement_obj = self.work_table.get(work_tuple)
        
        with self.equipment_manager.temporary_equipment(self.movement_equipment,handler):
        
            self._move_to_entity(base_work = work ,
                                move_obj = work_movement_obj
                                )
        