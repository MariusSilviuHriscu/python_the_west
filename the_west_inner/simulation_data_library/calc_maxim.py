import itertools
import typing
import random


from the_west_inner.game_classes import Game_classes
from the_west_inner.item_set_general import get_item_sets

from the_west_inner.simulation_data_library.simul_items import Item_model_list,create_item_list_from_model,Item_model
from the_west_inner.simulation_data_library.simul_equipment import Equipment_simul
from the_west_inner.simulation_data_library.simul_sets import Item_set_list
from the_west_inner.simulation_data_library.simul_equip_fitnes import SimulFitnessRuleSet
from the_west_inner.simulation_data_library.load_items_script import get_simul_items,get_simul_sets
from the_west_inner.simulation_data_library.simul_equipment import _game_data_to_current_equipment
from the_west_inner.simulation_data_library.simul_permutation_data import EquipmentPermutationData


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
class Brute_force_simulation_bonus_check():
    def __init__(self,equipment_reader:Equipment_simul,item_model_list:Item_model_list,set_model_list:Item_set_list):
        self.equipment_reader = equipment_reader
        self.item_model_list = item_model_list
        self.set_model_list = set_model_list
    
    def possible_equipment_generator(self) -> typing.Generator[EquipmentPermutationData,None,None]:
        item_type_dict = self.item_model_list.get_item_dict()
        permutation_generator = Equipment_permutation_generator(equipment_dictionary = item_type_dict).get_dict_permutations()
        for equipment_permutation in permutation_generator:
            for item_type,item in equipment_permutation.items():
                
                self.equipment_reader.replace_item(
                                                    replaced_item =  self.equipment_reader.get_by_key(key = item_type),
                                                    replacement_item = item
                                                    )
            
            yield EquipmentPermutationData(
                **self.equipment_reader.create_status_dict(),
                   **{"permutation" : equipment_permutation})

    def maximum_equipment_value_brute_force(self,simul_rule_set : SimulFitnessRuleSet) -> EquipmentPermutationData|None :
        
        maximum = simul_rule_set.generate_empty_result()
        result_permutation = None
        
        for equip_permutation_data in self.possible_equipment_generator():
            
            result = simul_rule_set.get_fitness_result(equipment_data = equip_permutation_data)
            
            if result > maximum:
                
                maximum = result
                result_permutation = equip_permutation_data
        
        return result_permutation
    
    def _get_max_item(self,simul_rule_set : SimulFitnessRuleSet ,item_list : list[Item_model]) -> Item_model:
        
        equipment = self.equipment_reader.copy()
        maximum = simul_rule_set.generate_empty_result()
        max_item = None
        for item in item_list:
            equipment.empty()
            equipment.replace_item(replacement_item = item)
            
            result = simul_rule_set.get_fitness_result(equipment_data = equipment)
            if result >= maximum :
                maximum = result
                max_item = item
        
        return max_item
    
    def maximum_equipment_greedy(self, simul_rule_set: SimulFitnessRuleSet) ->EquipmentPermutationData|None:
        item_type_dict = self.item_model_list.get_item_dict()
        
        target_equipment_list = {item_type : self._get_max_item(simul_rule_set=simul_rule_set,item_list=same_item_list)
                                        for item_type,same_item_list in item_type_dict.items()
        }
        self.equipment_reader.empty()
        for equipment_item in target_equipment_list.values():
            if equipment_item is not None:
                self.equipment_reader.replace_item(replacement_item = equipment_item)
        return EquipmentPermutationData(
                **self.equipment_reader.create_status_dict(),
                   **{"permutation" : target_equipment_list})
        
class Item_cycle_simulation():
    def __init__(self,equipment_reader:Equipment_simul,item_model_list:Item_model_list,set_model_list:Item_set_list):
        self.equipment_reader = equipment_reader
        self.item_model_list = item_model_list
        self.set_model_list = set_model_list
    def sort_items(self,player_level : int) -> Item_model_list:
        return self.item_model_list.filter_mapdrop_items(
                        ).filter_out_usables(
                        ).filter_by_player_level(
                            player_level = player_level
                            )
    def brute_force(self , simul_rule_set: SimulFitnessRuleSet,player_level : int) -> EquipmentPermutationData:
        
        return Brute_force_simulation_bonus_check(
            equipment_reader= self.equipment_reader,
            item_model_list = self.sort_items(player_level=player_level),
            set_model_list= self.set_model_list
        ).maximum_equipment_value_brute_force(simul_rule_set=simul_rule_set)
    
    def greedy_sort(self, simul_rule_set : SimulFitnessRuleSet , player_level : int) -> EquipmentPermutationData:
        
        return Brute_force_simulation_bonus_check(
            equipment_reader = self.equipment_reader,
            item_model_list = self.sort_items(player_level=player_level),
            set_model_list = self.set_model_list
        ).maximum_equipment_greedy(simul_rule_set=simul_rule_set)

