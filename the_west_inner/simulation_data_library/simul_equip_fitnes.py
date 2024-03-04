import typing
from typing import Protocol

from the_west_inner.simulation_data_library.simul_permutation_data import EquipmentPermutationData

class SimulFitnessRule(Protocol):
    def __init__(self):
        pass
    def calculate(self,equipment_data:EquipmentPermutationData) -> int:
        pass


class SimulResultFitness:
    def __init__(self, percent_coefficient=0.0):
        self.result = []
        self.percent_coefficient = percent_coefficient

    def append_result(self, result):
        self.result.append(result)

    

    def __lt__(self, other: typing.Self) -> bool:
        current_offset_percentage = self.percent_coefficient
        result_fitness_length = len(self.result)

        for index, (x, y) in enumerate(zip(self.result, other.result)):
            if x < y * (1 - current_offset_percentage):
                return True
            elif y > x > y * (1 - current_offset_percentage):
                if index + 1 < result_fitness_length:
                    if other.result[index + 1] < self.result[index + 1] * (1 - current_offset_percentage):
                        return False
                    else:
                        return True
                else:
                    return True
            elif x > y:
                return False
        return False  # All elements are equal


    def __gt__(self, other: typing.Self) -> bool:
        current_offset_percentage = self.percent_coefficient
        result_fitness_length = len(self.result)
        
        for index, (x, y) in enumerate(zip(self.result, other.result)):
            if x > y * (1 + current_offset_percentage):
                return True
            elif y < x < y * (1 + current_offset_percentage):
                if index + 1 < result_fitness_length:
                    if other.result[index + 1] > self.result[index + 1] * (1 + current_offset_percentage):
                        return False
                    else:
                        return True
                else:
                    return True
            elif x < y :
                return False
        return False  # All elements are equal
                    
    def __eq__(self, other: typing.Self) -> bool:
        return all((x == y for x, y in zip(other.result, self.result)))

    def __ne__(self, other: typing.Self) -> bool:
        return not self.__eq__(other)

    def __le__(self, other: typing.Self) -> bool:
        return self.__lt__(other) or self.__eq__(other)
    
    def __ge__(self, other: typing.Self) -> bool:
        return self.__gt__(other) or self.__eq__(other)

class SimulFitnessRuleSet():
    
    def __init__(self , fitness_rule_list : list[SimulFitnessRule]|None):
        
        self.fitness_rule_list = fitness_rule_list
        if fitness_rule_list is None:
            self.fitness_rule_list = []
    def generate_empty_result(self) -> SimulResultFitness:
        
        result_fitness = SimulResultFitness()
        
        for _ in self.fitness_rule_list:
            
            result_fitness.append_result(result=0)
        
        return result_fitness
        
    def calculate_total(self,equipment_data : EquipmentPermutationData) -> int:
        
        return sum(
            (x.calculate(equipment_data = equipment_data) for x in self.fitness_rule_list)
        )
    def get_fitness_result(self,equipment_data : EquipmentPermutationData ) -> SimulResultFitness:
        
        result = SimulResultFitness()
        
        for rule in self.fitness_rule_list:
            
            rule_result  = rule.calculate(equipment_data = equipment_data)
            result.append_result(result = rule_result)

        return result