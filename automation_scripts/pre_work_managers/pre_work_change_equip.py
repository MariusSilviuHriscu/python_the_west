import time
import typing
from dataclasses import dataclass

from the_west_inner.requests_handler import requests_handler
from the_west_inner.equipment import Equipment,SavedEquipment,SavedEquipmentManager,Equipment_manager


@dataclass
class EquipmentChangeCollection:
    
    work_equipment : Equipment | SavedEquipment | int | str
    reward_equipment : Equipment | SavedEquipment | int | str
    
    @property
    def loaded(self) -> bool:
        
        return (type(self.work_equipment) not in [ int , str]
                and type(self.reward_equipment) not in [ int , str]
        )
    def load(self , saved_equip_manager : SavedEquipmentManager):
        
        if type(self.work_equipment) == int:
            value = saved_equip_manager.get_saved_equipment_by_id(equipment_id= self.work_equipment)
            if value is None:
                raise Exception('Invalid load id for saved equipment ')
            self.work_equipment = value
        if type(self.work_equipment) == str:
            value = saved_equip_manager.get_saved_equipment_by_name(equipment_name = self.work_equipment)
            if value is None:
                raise Exception('Invalid load name for saved equipment ')
            self.work_equipment = value
        
        if type(self.reward_equipment) == int:
            value = saved_equip_manager.get_saved_equipment_by_id(equipment_id= self.reward_equipment)
            if value is None:
                raise Exception('Invalid load id for saved equipment ')
            self.reward_equipment = value
        if type(self.reward_equipment) == str:
            value = saved_equip_manager.get_saved_equipment_by_name(equipment_name = self.reward_equipment)
            if value is None:
                raise Exception('Invalid load name for saved equipment ')
            self.reward_equipment = value
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
        
        if work_flag and isinstance(self.equipment_collection.work_equipment , SavedEquipment):
            
            self.equipment_manager.equip_saved_equipment(saved_equipment = self.equipment_collection.work_equipment,
                                                         handler=self.handler)
            return
        
        if not work_flag and isinstance(self.equipment_collection.reward_equipment , SavedEquipment):
            
            self.equipment_manager.equip_saved_equipment(saved_equipment = self.equipment_collection.reward_equipment,
                                                         handler= self.handler)
            return
        self.equipment_manager.equip_equipment_concurrently(
            equipment = self.equipment_collection.work_equipment if work_flag else self.equipment_collection.reward_equipment,
            handler = self.handler,
            retry_count= 3
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
        
        return PreWorkEquipChanger(
            equipment_collection = equip_collection,
            handler = self.handler,
            equipment_manager= self.equipment_manager
        )