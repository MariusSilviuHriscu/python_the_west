import typing
from dataclasses import dataclass

from ..premium import Premium
from simul_equipment import Equipment_simul
from simul_work_relevant_bonuses import Work_bonuses

PLAYER_PREMIUM_SALARY_COEFICIENT = 0.5
PLAYER_PREMIUM_CHARACTER_COEFICIENT = 2

class Player_data():
    def __init__(self,inventory:Equipment_simul,premium:Premium,consumable_bonus :Work_bonuses = Work_bonuses() , class_bonuses : Work_bonuses = Work_bonuses()):
        self.inventory = inventory
        self.premium = premium
        self.consumable_bonus = consumable_bonus
        self.class_bonuses = class_bonuses
    
    def generate_work_bonuses(self) -> Work_bonuses:
        premium_salary_bonus = Work_bonuses()
        if self.premium.money:
            premium_salary_bonus = Work_bonuses(
                                                product_drop = PLAYER_PREMIUM_SALARY_COEFICIENT,
                                                item_drop = PLAYER_PREMIUM_SALARY_COEFICIENT,
                                                salary_bonus = PLAYER_PREMIUM_SALARY_COEFICIENT
                                                )
        if self.premium.character:
            keys = [x for x,y in self.class_bonuses.__dict__.items() if y!= 0]
            self.class_bonuses.add_mult_attribute_list(attribute_list = keys,factor = PLAYER_PREMIUM_CHARACTER_COEFICIENT)
        return self.inventory.work_bonuses + self.class_bonuses + premium_salary_bonus + self.consumable_bonus