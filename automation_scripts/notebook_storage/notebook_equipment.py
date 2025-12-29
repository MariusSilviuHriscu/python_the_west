import json

from the_west_inner.equipment import Equipment_manager,Equipment
from the_west_inner.notebook import Notebook

class NotebookEquipSaver:
    
    def __init__(self,
                 equipment_manager : Equipment_manager ,
                 notebook : Notebook
    ):
        self.equipment_manager = equipment_manager
        self.notebook = notebook
    
    def save_current_equipment(self ):
        
        current_equipment = {x:y for x,y in self.equipment_manager.current_equipment}
        equipment_json = json.dumps(current_equipment)
        
        self.notebook.edit(new_text = equipment_json)
    
    def get_notebook_equipment(self) -> Equipment | None:
        
        equipment_str = self.notebook.content
        if equipment_str is None:
            return None
        
        try:
            return Equipment(
                ** json.loads(equipment_str)
            )
        except json.JSONDecodeError as e:
            return None