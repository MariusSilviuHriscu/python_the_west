
from the_west_inner.simulation_data_library.simul_skills import CharacterSkillsEnum
from the_west_inner.simulation_data_library.calc_maxim import EquipmentPermutationData

class WorkSkillsSimulRule:
    
    def __init__(self, skill_dict : dict[CharacterSkillsEnum,int]):
        
        self.skill_dict = skill_dict
        
    def calculate(self, equipment_data : EquipmentPermutationData):
        total_skill_numbers = 0
        equipment_skills = equipment_data.status.effective_skills
        
        for skill,skill_number in self.skill_dict.items():
            respective_equipment_skills = equipment_skills[str(skill)]

            total_skill_numbers  += respective_equipment_skills * skill_number
        
        return total_skill_numbers