import itertools
import typing

from the_west_inner.simulation_data_library.simul_items import Item_model_list,create_item_list_from_model
from the_west_inner.simulation_data_library.simul_equipment import Equipment_simul,Equipment_analysis_tool
from the_west_inner.simulation_data_library.simul_sets import Item_set_list
from the_west_inner.simulation_data_library.load_items_script import get_simul_items


from ..bag import Bag
from ..items import Items
from ..equipment import Equipment
from ..item_set_general import Item_sets


class Simulation_data_loader():
    def __init__(self,bag:Bag,items:Items,sets:Item_sets,current_equipment:Equipment,player_level:int):
        self.bag = bag
        self.items = items
        self.sets = sets
        self.current_equipment = current_equipment
        self.player_level = player_level
    def assemble_item_list_from_game_data(self):
        item_list = create_item_list_from_model(
                                        item_model_list = get_simul_items(
                                                                        bag = self.bag,
                                                                        current_equipment = self.current_equipment,
                                                                        items = self.items),
                                        player_level= self.player_lever
                                        )
        return item_list
    def assemble_item_sets_from_game_data(self):
        pass

class Equipment_permutation_generator():
    def __init__(self,equipment_dictionary: dict[str,int]) -> None:
        #self.equipment_dict = {x:lambda f : f if f!= [] else [None](y) for x,y in equipment_dictionary.items()}
        #Why?!?!?!? Solve this riddle
        self.equipment_dict = equipment_dictionary
    
    def get_dict_permutations(self):
        keys = list(
                    self.equipment_dict.keys()
                    )
        values = list(
                        itertools.product(
                                            *self.equipment_dict.values()
                                        )
                    )
        for v in values:
            yield dict(zip(keys, v))
    def get_dict_permutations(self):
        keys = list(
                    self.equipment_dict.keys()
                    )
        values = [self.equipment_dict[key] for key in keys]
        permutations = list(itertools.product(*values))
        for perm in permutations:
            yield {keys[i]: perm[i] for i in range(len(keys))}
class Greedy_simulation_bonus_check():
    def __init__(self,equipment_reader:Equipment_simul,item_model_list:Item_model_list,set_model_list:Item_set_list):
        self.equipment_reader = equipment_reader
        self.item_model_list = item_model_list
        self.set_model_list = set_model_list
    
    def possible_equipment_generator(self) -> typing.Generator:
        item_type_dict = self.item_model_list.get_item_dict()
        permutation_generator = Equipment_permutation_generator(equipment_dictionary = item_type_dict).get_dict_permutations()
        for equipment_permutation in permutation_generator:
            for item_type,item in equipment_permutation.items():
                
                self.equipment_reader.replace_item(
                                                    replaced_item =  self.equipment_reader.get_by_key(key = item_type),
                                                    replacement_item = item
                                                    )
            yield self.equipment_reader.copy()
    def maximul_equipment_value(self,value_key:str,minimum_value:typing.Any):
        maximum_value = minimum_value
        maximum_equipment = None
        equipment_generator = self.possible_equipment_generator()
        for equipment_data in equipment_generator:
            if getattr(value_key,equipment_data) > maximum_value:
                maximum_value = getattr(value_key,equipment_data)
                maximum_equipment = equipment_data
        return maximum_equipment
class Item_cycle_simulation():
    def __init__(self,equipment_reader:Equipment_simul,item_model_list:Item_model_list,set_model_list:Item_set_list):
        self.equipment_reader = equipment_reader
        self.item_model_list = item_model_list
        self.set_model_list = set_model_list
    def greedy(self,check_for_bonus:str) -> Greedy_simulation_bonus_check:
        target_set_keys_list : list = self.set_model_list.filter_by_bonus(attribute_key = check_for_bonus).return_set_key_list()
        return Greedy_simulation_bonus_check(
                                            equipment_reader = self.equipment_reader,
                                            item_model_list = self.item_model_list.filter_by_item_id_list(sets = target_set_keys_list),
                                            set_model_list = self.set_model_list
                                            )