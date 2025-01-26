from the_west_inner.simulation_data_library.calc_maxim import EquipmentPermutationData

class SalarySimulRule:

    def __init__(self ):
        pass
    def calculate(self, equipment_data : EquipmentPermutationData) -> int:
        
        return equipment_data.status.additional_iterator