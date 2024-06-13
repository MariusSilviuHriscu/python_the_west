from the_west_inner.skills import CharacterSkillsEnum
from the_west_inner.simulation_data_library.calc_maxim import EquipmentPermutationData

class TotalSkillPointsRule:
            
    def calculate(self, equipment_data : EquipmentPermutationData):
        equipment_skills = equipment_data.status.effective_skills
        skill_names = CharacterSkillsEnum.get_all_skills()
        
        return sum(
            (equipment_skills[x]  for x in skill_names)
        )