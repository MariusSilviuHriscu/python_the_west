import copy


from simul_items import Item,Animal,Belt,Clothes,Pants,Boots,Headgear,Weapon,Necklace,Fort_weapon,Produs,Item_model,create_item_list_from_model,Item_model_list,create_item_list_from_model
from simul_sets import Item_set,create_set_instance_list,Item_set_list
#from simul_skills import Skills
from simul_work_relevant_bonuses import Work_bonuses
from the_west_inner.item_set_general import get_item_sets
from the_west_inner.simulation_data_library.load_items_script import get_simul_items, get_simul_sets

from ..equipment import Equipment
class Equipment_analysis_tool():
    def __init__(self, player_level:int,item_list:Item_model,item_set_list:Item_set_list):
        self.player_level = player_level
        self.item_list = [ x for x in item_list if x is not None ]
        self.item_set_list = item_set_list
        self.set_list = self.calc_sets()
        self.analysis_item_tool = None
        self.analysis_set_tool = None
    def calc_sets(self) -> dict:
        sets = dict()
        final_sets = dict()
        for indiv_item in self.item_list:
            element  = indiv_item.item_set
            if element == "":
                continue
            if element is None:
                continue
            if element in sets:
                sets[element] += 1
            else:
                sets[element] = 1
        for set_name,set_value in sets.items():
            if str(set_value) in self.item_set_list.get(set_name).bonuses_dict_by_number:
                final_sets[set_name] = set_value
        return final_sets
    def _initialised_analysis_tools(self) -> bool:
        if self.analysis_item_tool is not None and self.analysis_set_tool is not None:
            return True
        return False
    def _initialise_analysis_tools(self) -> None:
        self.analysis_item_tool = create_item_list_from_model(
                                                        item_model_list= self.item_list ,
                                                        player_level = self.player_level
                                                    )
        self.analysis_set_tool = create_set_instance_list(
                                                        item_set_list = self.item_set_list,
                                                        number_set_dict = self.set_list,
                                                        player_level= self.player_level
                                                            )
    @property
    def item_drop(self):
        if not self._initialised_analysis_tools():
            self._initialise_analysis_tools()
        return self.analysis_item_tool.item_drop + self.analysis_set_tool.item_drop
    @property
    def workpoints(self):
        if not self._initialised_analysis_tools():
            self._initialise_analysis_tools()
        return self.analysis_item_tool.workpoints + self.analysis_set_tool.workpoints
    @property
    def product_drop(self):
        if not self._initialised_analysis_tools():
            self._initialise_analysis_tools()
        return self.analysis_item_tool.product_drop + self.analysis_set_tool.product_drop
    @property
    def regeneration(self):
        if not self._initialised_analysis_tools():
            self._initialise_analysis_tools()
        return self.analysis_item_tool.regeneration + self.analysis_set_tool.regeneration
    @property
    def damage(self):
        if not self._initialised_analysis_tools():
            self._initialise_analysis_tools()

        return self.analysis_item_tool.damage + self.analysis_set_tool.damage
    @property
    def speed(self):
        if not self._initialised_analysis_tools():
            self._initialise_analysis_tools()

        return self.analysis_item_tool.speed + self.analysis_set_tool.speed
    @property
    def exp_bonus(self):
        if not self._initialised_analysis_tools():
            self._initialise_analysis_tools()

        return self.analysis_item_tool.exp_bonus + self.analysis_set_tool.exp_bonus
    @property
    def work_bonuses(self) -> Work_bonuses:
        return Work_bonuses(
                            product_drop = self.product_drop,
                            item_drop = self.item_drop,
                            exp_bonus = self.exp_bonus,
                            salary_bonus = 0
                            )

class Equipment_simul():
    def __init__(self,
                 weapon:Weapon,
                 headgear:Headgear,
                 clothes:Clothes,
                 pants:Pants,
                 boots:Boots,
                 belt:Belt,
                 necklace:Necklace,
                 fort_weapon:Fort_weapon,
                 animal:Animal,
                 produs:Produs ,
                 item_set_list : Item_set_list ,
                 player_level:int = 0
                ):
        self.item_set_list = item_set_list
        self.player_level = player_level
        self.weapon = weapon
        self.headgear = headgear
        self.clothes = clothes
        self.pants = pants
        self.boots = boots
        self.belt = belt
        self.necklace = necklace
        self.fort_weapon = fort_weapon
        self.animal = animal
        self.produs = produs 
        self.analysis_tool = Equipment_analysis_tool(
                                                    player_level = self.player_level,
                                                    item_list = [self.weapon,
                                                                      self.headgear,
                                                                      self.clothes,
                                                                      self.pants,
                                                                      self.boots,
                                                                      self.belt,
                                                                      self.necklace,
                                                                      self.fort_weapon,
                                                                      self.animal,
                                                                      self.produs],
                                                    item_set_list = self.item_set_list
                                                    )


    @property
    def item_drop(self):
        return self.analysis_tool.item_drop
    @property
    def workpoints(self):
        return self.analysis_tool.workpoints
    @property
    def product_drop(self):
        return self.analysis_tool.product_drop
    @property
    def regeneration(self):
        return self.analysis_tool.regeneration
    @property
    def damage(self):
        return self.analysis_tool.damage
    @property
    def speed(self):
        return self.analysis_tool.speed
    @property
    def exp_bonus(self):
        return self.analysis_tool.exp_bonus
    @property   
    def weapon_damage(self):
        return self.weapon.weapon_damage + self.damage
    def get_by_key(self,key:str) -> Item_model:
        item_dict = {"weapon":self.weapon,
                     "headgear":self.headgear,
                     "clothes":self.clothes,
                     "pants":self.pants,
                     "boots":self.boots,
                     "belt":self.belt,
                     "necklace":self.necklace,
                     "fort_weapon":self.fort_weapon,
                     "animal":self.animal,
                     "produs":self.produs}
        return item_dict[key]
    def _swap_items(self,value1:Item,value2:Item) -> None:
        
        item_dict = {Weapon:'weapon',
                     Headgear:'headgear',
                     Clothes:'clothes',
                     Pants:'pants',
                     Boots:'boots',
                     Belt:'belt',
                     Necklace:'necklace',
                     Fort_weapon:'fort_weapon',
                     Animal:'animal',
                     Produs:'produs'}
        if value1 is None and value2 is None:
            raise Exception('Changing none to none is nonsense! Abort')
        
        
        
        if value1 is not None:
            for item_type in item_dict:
                if isinstance(value1,item_type):
                    setattr(self, item_dict[item_type],value2)
        else:
            for item_type in item_dict:
                if isinstance(value2,item_type):
                    setattr(self, item_dict[item_type],value2)
    def replace_item(self,replaced_item:Item = None, replacement_item:Item = None) -> None:
        if replaced_item is not None and replacement_item is not None and type(replacement_item) != type(replaced_item):
            raise ValueError("The equipment swap is not a valid one! ")
        
        self._swap_items(value1= replaced_item,value2= replacement_item)
        self.analysis_tool = Equipment_analysis_tool(
                                                    player_level = self.player_level,
                                                    item_list = [self.weapon,
                                                                      self.headgear,
                                                                      self.clothes,
                                                                      self.pants,
                                                                      self.boots,
                                                                      self.belt,
                                                                      self.necklace,
                                                                      self.fort_weapon,
                                                                      self.animal,
                                                                      self.produs] ,
                                                    item_set_list = self.item_set_list
                                                    )
    def copy(self):
        return copy.deepcopy(self)
    def pretty_print(self) -> str:
        return " ".join((str(x.item_id) for x in 
            [self.weapon,
             self.headgear,
             self.clothes,
             self.pants,
             self.boots,
             self.belt,
             self.necklace,
             self.fort_weapon,
             self.animal,
             self.produs] if x is not None))
def create_simul_equipment_by_current_equipment(current_equipment : Equipment,
                                                player_level : int,
                                                item_set_list : list[Item_set],
                                                bag_item_list : Item_model_list
                                                ) -> Equipment_simul :
    
    
    filtered_item_list = bag_item_list.filter_by_item_id_list(
                                            list(current_equipment.__dict__.values())
                                            )
    
    return Equipment_simul(
        weapon = filtered_item_list.get_model_by_id(current_equipment.right_arm_item_id) ,
        headgear = filtered_item_list.get_model_by_id(current_equipment.head_item_id) ,
        clothes = filtered_item_list.get_model_by_id(current_equipment.body_item_id) ,
        pants = filtered_item_list.get_model_by_id(current_equipment.pants_item_id) ,
        boots = filtered_item_list.get_model_by_id(current_equipment.foot_item_id) ,
        belt = filtered_item_list.get_model_by_id(current_equipment.belt_item_id) ,
        necklace = filtered_item_list.get_model_by_id(current_equipment.neck_item_id) ,
        fort_weapon = filtered_item_list.get_model_by_id(current_equipment.left_arm_item_id) ,
        animal = filtered_item_list.get_model_by_id(current_equipment.animal_item_id) ,
        produs = filtered_item_list.get_model_by_id(current_equipment.yield_item_id) ,
        item_set_list = Item_set_list(set_list = item_set_list) ,
        player_level = player_level
        )

def _game_data_to_current_equipment(game_data) -> Equipment_simul:
    raw_sets = get_item_sets(requests_handler= game_data.handler)
    sets = get_simul_sets(
                    sets= raw_sets
                    )
    list_of_item_models = get_simul_items(
                                    bag = game_data.bag,
                                    current_equipment = game_data.equipment_manager.current_equipment,
                                    items = game_data.items
                                    )
    item_model_list = Item_model_list(item_model_list = list_of_item_models)
    simul_equip = create_simul_equipment_by_current_equipment(
                                                        current_equipment = game_data.equipment_manager.current_equipment,
                                                        player_level = game_data.player_data.level,
                                                        item_set_list = sets,
                                                        bag_item_list = item_model_list
                                                        )
    
    return simul_equip