from automation_scripts.notebook_storage.notebook_equipment import NotebookEquipSaver

from the_west_inner.game_classes import Game_classes
from the_west_inner.bag import Bag
from the_west_inner.equipment import Equipment,Equipment_manager
from the_west_inner.notebook import Notebook
from the_west_inner.requests_handler import requests_handler

class NotebookChanger:
    
    def __init__(self , 
                 notebook_saver : NotebookEquipSaver,
                 equipment_manager : Equipment_manager,
                 regen_equip : Equipment,
                 bag : Bag
                 ):
        self.notebook_saver = notebook_saver
        self.equipment_manager = equipment_manager
        self.bag = bag
        
        self.regen_equip = regen_equip
    
    def has_item(self , item_id : int ) -> bool :
        
        return self.bag[item_id] != 0 or item_id in self.equipment_manager.current_equipment
    
    def has_items(self , equipment : Equipment) -> bool:
        
        return all(
            [self.has_item(item_id = x) for _,x in equipment]
        )
    
    def check_saved_equipment(self) -> bool:
        
        return self.notebook_saver.get_notebook_equipment() is not None
    
    def equip_regen(self,handler : requests_handler):
        
        if not self.has_items(equipment = self.regen_equip):
            
            return
        
        if not self.check_saved_equipment():
            
            self.notebook_saver.save_current_equipment()
        
        self.equipment_manager.equip_equipment(
            equipment = self.regen_equip,
            handler = handler
        )
    
    def equip_work(self, handler : requests_handler):
        
        if not self.check_saved_equipment():
            
            return
        
        self.equipment_manager.equip_equipment(
            equipment = self.notebook_saver.get_notebook_equipment(),
            handler= handler
        )

def build_notebook_changer(game_classes : Game_classes , regen_equip : Equipment) -> NotebookChanger:
    
    
    notebook_saver = NotebookEquipSaver(
        equipment_manager = game_classes.equipment_manager,
        notebook= Notebook(handler= game_classes.handler)
    )
    
    return NotebookChanger(
        notebook_saver= notebook_saver,
        equipment_manager= game_classes.equipment_manager,
        regen_equip = regen_equip,
        bag = game_classes.bag
    )