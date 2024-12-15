import copy
import typing
from contextlib import contextmanager
from dataclasses import dataclass
import concurrent.futures
import time

from the_west_inner.requests_handler import requests_handler
from the_west_inner.bag import Bag
from the_west_inner.skills import Skills
from the_west_inner.items import Items

Equipment_change_dict = typing.Dict[typing.Literal["head","neck","left_arm","body","right_arm","foot","animal","belt","pants"],int]

@dataclass
class Equipment:
    head_item_id: typing.Union[int, None] = None
    neck_item_id: typing.Union[int, None] = None
    left_arm_item_id: typing.Union[int, None] = None
    body_item_id: typing.Union[int, None] = None
    right_arm_item_id: typing.Union[int, None] = None
    foot_item_id: typing.Union[int, None] = None
    animal_item_id: typing.Union[int, None] = None
    belt_item_id: typing.Union[int, None] = None
    pants_item_id: typing.Union[int, None] = None
    yield_item_id: typing.Union[int, None] = None
    
    
    def change_equipment(self, change_equipment_dict: Equipment_change_dict) -> None:
        # Check for invalid item types
        valid_item_types = ["head_item_id", "neck_item_id", "left_arm_item_id", "body_item_id", "right_arm_item_id", "foot_item_id", "animal_item_id", "belt_item_id", "pants_item_id","yield_item_id"]
        invalid_item_types = [item_type for item_type in change_equipment_dict.keys() if item_type not in valid_item_types]
        if invalid_item_types:
            raise Exception(f"Invalid item type(s): {invalid_item_types}")
        
        # Check for overflow (too many items)
        overflow_item_types = [item_type for item_type, item in change_equipment_dict.items() if type(item)==list and len(item) >= 2]
        if len(overflow_item_types) != 0:
            raise Exception(f"Trying to add too many items of the following types: {overflow_item_types}")
        
        # Update equipment
        for item_type, item_id in change_equipment_dict.items():
            if item_id is not None:
                attribute_string_item = f'{item_type}' if f'{item_type}'.endswith('_item_id') else f"{item_type}_item_id"
                setattr(self, attribute_string_item, item_id)
    def unequip_item(self , item_type : str) :
        valid_item_types = ["head_item_id", "neck_item_id", "left_arm_item_id", "body_item_id", "right_arm_item_id", "foot_item_id", "animal_item_id", "belt_item_id", "pants_item_id","yield_item_id"]
        if item_type not in valid_item_types:
            raise ValueError(f'Invalid unequip type : {item_type}')
        setattr(self , item_type  , None)
    def __iter__(self):
        yield from vars(self).items()
    def __eq__(self, other: typing.Any) -> bool:
        if not isinstance(other, Equipment):
            raise TypeError(f"Cannot compare Equipment object to object of type {type(other)}")
        return vars(self) == vars(other)
    def __contains__(self,item_id:int) -> bool:
        return item_id in self.__dict__.values()
    def get_item_type_by_id(self, item_id : int) -> str:
        if item_id not in self:
            raise ValueError('The required item is not part of the equipment !')
        for item_type , equipment_item_id in self.__dict__.items():
            if equipment_item_id == item_id:
                return item_type

class SavedEquipment:
    
    def __init__(self ,
                 name : str ,
                 equipment_id : int,
                 equipment_items : Equipment
                 ):
        
        self.name = name
        self.equipment_id = equipment_id
        self.equipment_items = equipment_items
    
    @staticmethod
    def build_from_dict(input_dict : dict) -> typing.Self:
        
        equipment = Equipment(
            head_item_id = input_dict.get('head'),
            neck_item_id = input_dict.get('neck'),
            left_arm_item_id = input_dict.get('left_arm'),
            body_item_id= input_dict.get('body'),
            right_arm_item_id = input_dict.get('right_arm'),
            foot_item_id = input_dict.get('foot'),
            animal_item_id = input_dict.get('animal'),
            belt_item_id = input_dict.get('belt'),
            pants_item_id = input_dict.get('pants'),
            yield_item_id = input_dict.get('yield')
        )
        
        return SavedEquipment(
            name = input_dict.get('name'),
            equipment_id = input_dict.get('equip_manager_id'),
            equipment_items = equipment
        )
    
    def is_valid(self , bag : Bag) -> bool :
        
        return all( y in bag for _,y in self.equipment_items)
    

class SavedEquipmentManager:
    
    def __init__(self , 
                 handler : requests_handler ,
                 bag : Bag ):
        
        self.handler = handler
        self.bag = bag
        
        self._saved_equipment_list : None | list[SavedEquipment] = None
    
    @property
    def is_loaded(self) -> bool:
        
        return self._saved_equipment_list is not None
    
    
    def _load_saved_equipment(self , response_list : list[dict]) -> list[SavedEquipment]:
        
        return [
            SavedEquipment.build_from_dict(input_dict = x) for x in response_list
        ]
    def load_saved_equipment(self) -> None:
        
        response = self.handler.post(window = 'inventory',
                                     action= 'show_equip',
                                     action_name= 'mode'
                                     )
        
        self._saved_equipment_list =  self._load_saved_equipment(response_list = response.get('data'))
    
    def get_saved_equipment_by_id(self , equipment_id : int) -> SavedEquipment|None :
        
        if not self.is_loaded:
            
            self.load_saved_equipment()
            
        for saved_equip in self._saved_equipment_list:
            
            if saved_equip.equipment_id == equipment_id:
                return saved_equip
    def get_saved_equipment_by_name(self , equipment_name : str) -> SavedEquipment|None :
        
        if not self.is_loaded:
            
            self.load_saved_equipment()
            
        for saved_equip in self._saved_equipment_list:
            
            if saved_equip.name == equipment_name:
                return saved_equip
    
    def is_valid_saved_equipment(self , saved_equipment : SavedEquipment ) -> bool:
        
        return saved_equipment.is_valid(bag = self.bag)
        




class Equipment_manager():
    def __init__(self,current_equipment:Equipment,bag:Bag,items:Items,skills:Skills):
        self.current_equipment = current_equipment
        self.bag = bag
        self.items = items
        self.skills = skills
    def equip_item(self,item_id:int,handler:requests_handler) -> dict:
        #replace_last_char = lambda s: str(s)[:-1] + "0"
        if item_id not in self.items:
            raise Exception(f"You tried to equip item that does not exist! : {item_id} ")
        if item_id not in self.bag :
            raise Exception(f"You tried to equip something you do not have in your inventory: {item_id}")
        response =  handler.post(
            window= "inventory",
            action= "carry",
            payload= {
                'item_id': f"{item_id}"
                },
            use_h= True
        )
        
        if response['error'] :
            raise Exception(f"Error when trying to equip id_{item_id} : {response['error']}")
        
        return response
    def _unequip_item(self , 
                     item_id : int ,
                     handler : requests_handler
                     ) -> dict:
        
        
        response = handler.post(
            window = 'inventory',
            action = 'uncarry',
            payload={
                'last_inv_id' : self.bag.last_inv_id ,
                'type' : self.items.find_item(item_id = item_id).get('type')
            },
            use_h= True
        )
        
        if 'error' in response and response['error'] :
            raise Exception(f"Error when trying to unequip id_{item_id} : {response['error']}")
        
        return response
    
    def unequip_item(self , item_id : int , handler : requests_handler) -> bool:
        if item_id not in self.items:
            raise Exception(f"You tried to unequip item that does not exist! : {item_id} ")
        if item_id not in self.current_equipment:
            raise Exception(f"You tried to unequip something you do not have equipped: {item_id}")
        
        equipment_type = self.current_equipment.get_item_type_by_id(item_id = item_id)
        
        response = self._unequip_item(item_id = item_id , handler= handler)
        
        self.bag.add_item(item_id = item_id ,amount= 1)
        self.current_equipment.unequip_item(item_type = equipment_type)
        self.equipment_change_skill_update(
            skill_change= response['bonus']['allBonuspoints']
        )
        
        return True
    
    def equipment_change_skill_update(self,skill_change:dict)->None:
        self.skills.set_skills_and_attributes_bonus(change_dict=skill_change)
    def equip_equipment(self,equipment:Equipment,handler:requests_handler):
        response = dict()
        for item_type,item in equipment :
            if item is None :
                continue
            if item in self.current_equipment:
                continue
            response = self.equip_item(item_id=item,handler=handler)
            self.bag.consume_item(item_id= item)
            self.bag.add_item(
                item_id=getattr(self.current_equipment,f'{item_type}'),
                amount=1
                )
            self.current_equipment.change_equipment(change_equipment_dict={item_type:item})
            #time.sleep(1)
        if response == {}:
            return False
        self.equipment_change_skill_update(
            skill_change= response['bonus']['allBonuspoints']
        )
        return True
    def equip_equipment_concurrently(self, equipment: Equipment, handler: requests_handler):
        start_time = time.time()  # Start timing
        responses = []
        
        # Define the function for equipping a single item
        def equip_single_item(item_type, item_id):
            # Check if the item needs to be equipped
            if item_id is None or item_id in self.current_equipment:
                return None  # Skip None items or items that are already equipped

            # Send the equip request
            response = self.equip_item(item_id=item_id, handler=handler)
            
            # Consume the equipped item and update the current equipment
            self.bag.consume_item(item_id=item_id)
            self.bag.add_item(item_id=getattr(self.current_equipment, f'{item_type}'), amount=1)
            self.current_equipment.change_equipment({item_type: item_id})
            
            return response
        
        # Use ThreadPoolExecutor to equip items concurrently
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit all equipment tasks to the executor
            futures = {
                executor.submit(equip_single_item, item_type, item): item_type
                for item_type, item in equipment if item is not None and item not in self.current_equipment
            }

            # Wait for all futures to complete and gather their results
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    responses.append(result)
        
        # End timing
        end_time = time.time()
        total_time = end_time - start_time
        #print(f"Time taken to equip equipment concurrently: {total_time:.2f} seconds")
        
        # Check for successful responses
        if not responses:
            return False  # No items were equipped
        # Assuming all responses have similar skill changes
        # Only updating skills once with the last response's skill change
        last_response = responses[-1]
        self.equipment_change_skill_update(skill_change=last_response['bonus']['allBonuspoints'])
        
        return True
    
    def _equip_saved_equipment(self , saved_equipment : SavedEquipment , handler : requests_handler) -> dict:
        payload = {
            'id': saved_equipment.equipment_id,
            'last_inv_id': self.bag.last_inv_id
        }
        response = handler.post(
            window = 'inventory',
            action= 'switch_equip',
            payload= payload,
            use_h= True
        )
        
        if response.get('error') :
            raise Exception('Something went wrong when trying to equip a saved equipment ! ')
        
        return response

    def equip_saved_equipment(self , saved_equipment : SavedEquipment , handler : requests_handler):
        
        changes = self._equip_saved_equipment(
            saved_equipment=saved_equipment,
            handler=handler
        )
        
        
        for _ , item_id in self.current_equipment:
            
            self.bag.add_item(item_id = item_id)
            
        self.current_equipment.change_equipment(
            change_equipment_dict= {x:y for x,y in saved_equipment.equipment_items}
        )
        
        for _ , item_id in self.current_equipment:
            
            self.bag.consume_item(item_id = item_id)
        
        self.equipment_change_skill_update(skill_change=changes['bonus']['allBonuspoints'])
        
        return True
    
    @contextmanager
    def temporary_equipment(self, new_equipment: Equipment | SavedEquipment, handler: requests_handler):
        # Step 1: Save the current equipment state
        
        old_equipment = copy.deepcopy(self.current_equipment)

        try:
            # Step 2: Equip the new equipment
            if isinstance(new_equipment , SavedEquipment):
                self.equip_saved_equipment(saved_equipment= new_equipment , handler= handler)
            else :
                self.equip_equipment_concurrently(new_equipment, handler)
            yield
        finally:
            # Step 3: Re-equip the old equipment when exiting the context
            self.equip_equipment_concurrently(old_equipment, handler)
        
        
def create_initial_equipment(item_list:typing.List[int],items:Items) -> Equipment:
    #Make sure the item_id is the basic one as the last character in the id reprezents the upgrade of the item
    #replace_last_char = lambda s: s#str(s)[:-1] + "0"

    item_to_item_type_dict ={items.get_item(x)['type'] : x for x in item_list}
    return Equipment(
        head_item_id = item_to_item_type_dict.get('head' , None) ,
        neck_item_id = item_to_item_type_dict.get('neck' , None) ,
        left_arm_item_id = item_to_item_type_dict.get('left_arm' , None) ,
        body_item_id = item_to_item_type_dict.get('body' , None) ,
        right_arm_item_id = item_to_item_type_dict.get('right_arm' , None) ,
        foot_item_id = item_to_item_type_dict.get('foot' , None) ,
        animal_item_id = item_to_item_type_dict.get('animal' , None) ,
        belt_item_id = item_to_item_type_dict.get('belt' , None) ,
        pants_item_id = item_to_item_type_dict.get('pants' , None) ,
        yield_item_id = item_to_item_type_dict.get('yield',None)
    )