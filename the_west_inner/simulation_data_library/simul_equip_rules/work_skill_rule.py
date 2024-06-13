from the_west_inner.work_list import Work_list

from the_west_inner.skills import CharacterSkillsEnum
from the_west_inner.simulation_data_library.calc_maxim import EquipmentPermutationData

class WorkSkillDictSimulRule:
    
    def __init__(self, skill_dict : dict[CharacterSkillsEnum,int]):
        
        self.skill_dict = skill_dict
        
    def calculate(self, equipment_data : EquipmentPermutationData):
        total_skill_numbers = 0
        equipment_skills = equipment_data.status.effective_skills
        
        for skill,skill_number in self.skill_dict.items():
            respective_equipment_skills = equipment_skills[str(skill)]

            total_skill_numbers  += respective_equipment_skills * skill_number
        
        return total_skill_numbers + equipment_data.workpoints

class WorkSkillPointsRule:
    def __init__(self , work_id : int , work_job_data : Work_list):
        
        self.work_id = work_id
        self.work_job_data = work_job_data

    def calculate(self, equipment_data : EquipmentPermutationData):
        
        total_skill_numbers = 0
        equipment_skills = equipment_data.status.effective_skills
        work_skills_dict = self.work_job_data.get_work_skill_dict( work_id= self.work_id)
        
        for skill,skill_number in work_skills_dict.items():
            respective_equipment_skills = equipment_skills[skill]
            total_skill_numbers  += respective_equipment_skills * skill_number
        
        return total_skill_numbers