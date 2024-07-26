from the_west_inner.simulation_data_library.calc_maxim import EquipmentPermutationData


class LuckSimulRule:

    def __init__(self ):
        pass
    def calculate(self, equipment_data : EquipmentPermutationData) -> int:
        
        return equipment_data.item_drop

class ProductDropSimulRule :
    
    def __init__(self) -> None:
        pass
    
    def calculate(self , equipment_data : EquipmentPermutationData) -> int:
        
        return equipment_data.product_drop