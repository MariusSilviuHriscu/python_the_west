from the_west_inner.simulation_data_library.calc_maxim import EquipmentPermutationData

AIM_ATTACK_VALUE_DICT = {
    'aim' : 1,
    'dodge' : 1,
    'shot' : 0.75 ,
    'aspect' : 0.75,
    'hp' : 0.5
}


class AimShootAttackSimulRule:

    def __init__(self ):
        pass
    def calculate(self, equipment_data : EquipmentPermutationData) -> int:
        
        value : int = (
            equipment_data.status.dexterity_based_skills.aim * AIM_ATTACK_VALUE_DICT.get('aim') +
            equipment_data.status.dexterity_based_skills.shot * AIM_ATTACK_VALUE_DICT.get('shot') +
            equipment_data.status.mobility_based_skills.dodge * AIM_ATTACK_VALUE_DICT.get('dodge') +
            equipment_data.status.charisma_based_skills.appearance * AIM_ATTACK_VALUE_DICT.get('aspect') +
            equipment_data.status.strength_based_skills.health * AIM_ATTACK_VALUE_DICT.get('hp')
            )
        
        return value
        
        