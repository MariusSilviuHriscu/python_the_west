import typing
from dataclasses import dataclass

from the_west_inner.requests_handler import requests_handler
from the_west_inner.equipment import Equipment,Equipment_manager


@dataclass
class EquipmentChangeCollection:
    
    work_equipment : Equipment
    reward_equipment : Equipment


WorkIdType = int

class PreWorkEquipChanger:
    def __init__(self , 
                 equipment_collection : EquipmentChangeCollection,
                 handler : requests_handler ,
                 equipment_manager : Equipment_manager
    ):
        
        self.handler = handler
        self.equipment_manager= equipment_manager
        self.equipment_collection = equipment_collection
    
    def _handle_change(self , work_flag : bool):
        
        
        print(self.equipment_collection.work_equipment if work_flag else self.equipment_collection.reward_equipment)
        
        self.equipment_manager.equip_equipment(
            equipment = self.equipment_collection.work_equipment if work_flag else self.equipment_collection.reward_equipment,
            handler = self.handler
        )
    
    def handle_work(self ):
        
        self._handle_change(
                            work_flag = True
                            )
    def handle_reward(self):
        
        self._handle_change(
            work_flag= False
        )

class PreWorkEquipChangerManager:
    
    
    def __init__(self , 
                 work_equipment_table : dict[WorkIdType : EquipmentChangeCollection ],
                 handler : requests_handler ,
                 equipment_manager : Equipment_manager
    ):
        
        self.handler = handler
        self.equipment_manager= equipment_manager
        self.work_equipment_table = work_equipment_table
    
    def get_changer(self , work_id : int ) -> PreWorkEquipChanger:
        
        if work_id not in self.work_equipment_table:
            raise ValueError(f'The work id {work_id} cannot be found in the dict')
        
        equip_collection : EquipmentChangeCollection = self.work_equipment_table.get(work_id)
        print('generated changer')
        
        return PreWorkEquipChanger(
            equipment_collection = equip_collection,
            handler = self.handler,
            equipment_manager= self.equipment_manager
        )