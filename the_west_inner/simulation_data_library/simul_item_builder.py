from simul_bonus_item import Bonus_checker_complete
from simul_sets import Item_set_item_model
from simul_items import Animal,Belt,Clothes,Pants,Boots,Headgear,Weapon,Necklace,Fort_weapon,Produs,Item_update_table,Weapon_damage_range
from simul_skills import Skills

def create_null_skill():
    return Skills.null_skill()

class Item_builder():
    item_type = {'animal': Animal,
                 'belt': Belt,
                 'body': Clothes,
                 'pants': Pants,
                 'foot': Boots,
                 'head': Headgear,
                 'left_arm': Fort_weapon,
                 'neck': Necklace,
                 'right_arm': Weapon,
                 'yield': Produs,
                 'recipe': Produs,
                 'collection': Produs,
                 'weapon': Weapon
                 }
    def __init__(self,item_specific_dict:dict):
        self.item_specific_dict = item_specific_dict
        self.update_table = Item_update_table(*[False for _ in range(8)])
        self.item = self.item_type[self.item_specific_dict['type']
                                   ](name='',
                                     item_id='',
                                     value=0,
                                     status=create_null_skill(),
                                     item_set='',
                                     updates=self.update_table,
                                     level=0,
                                     item_drop=0,
                                     product_drop=0,
                                     workpoints=0,
                                     regeneration=0,
                                     damage=0,
                                     speed=0,
                                     exp_bonus=0,
                                     dropable=False,
                                     sellable=False,
                                     actionable=False,
                                     upgradeable=False
                                     )
        speed = self.check_item_speed()
        if speed is not None:
            self.item.speed = float(speed)
    def set_item_id(self):
        self.item.item_id = self.item_specific_dict['item_id']
    def set_item_name(self):
        self.item.name = self.item_specific_dict['name']
    def set_item_value(self):
        self.item.value = self.item_specific_dict['price']
    def set_item_damage_range(self):
        if isinstance(self.item,Weapon):
            damage_dict = self.item_specific_dict.get('damage')
            min_damage = damage_dict.get('damage_min')
            max_damage = damage_dict.get('damage_max')
            self.item.weapon_damage = Weapon_damage_range(min_damage=min_damage,
                                                          max_damage = max_damage
                                                          )
    def set_item_level(self):
        self.item.level = self.item_specific_dict['level']
    def set_item_set(self):
        self.item.item_set = self.item_specific_dict['set']
    def set_sellable(self):
        self.item.sellable = self.item_specific_dict['sellable']
    def set_auctionable(self):
        self.item.auctionable = self.item_specific_dict['auctionable']
    def check_item_speed(self):
        if 'speed' in self.item_specific_dict:
            return self.item_specific_dict['speed']
        else:
            return None
    def set_item_bonuses(self):
        checker = Bonus_checker_complete(self.item , self.item_specific_dict['bonus'])
        checker.check_inbuilt_bonus()
        checker.check_item_bonus()
    def set_dropable(self):
        self.item.dropable = self.item_specific_dict['dropable']
    def build_all(self) -> Animal|Belt|Clothes|Pants|Boots|Headgear|Weapon|Necklace|Fort_weapon|Produs:
        self.set_item_id()
        self.set_item_name()
        self.set_item_value()
        self.set_item_level()
        self.set_item_set()
        self.set_sellable()
        self.set_auctionable()
        self.set_item_bonuses()
        self.set_dropable()
        self.set_item_damage_range()
        return self.item

class Item_set_stage_builder():
    def __init__(self,stage_specific_dict:dict):
        self.stage_specific_dict = { "attributes": [],
                                    "skills": [],
                                    "fortbattle": {
                                            "offense": 0,
                                            "defense": 0,
                                            "resistance": 0
                                    },
                                    "fortbattlesector": {
                                        "defense": 0,
                                        "offense": 0,
                                        "damage": 0
                                    },
                                    "item": stage_specific_dict }
        self.update_table = Item_update_table(*[False for _ in range(8)])
        self.item = Item_set_item_model(
                                        updates= self.update_table,
                                        status= create_null_skill(),
                                        item_drop= 0,
                                        product_drop= 0 ,
                                        workpoints= 0 ,
                                        regeneration= 0 ,
                                        damage= 0,
                                        speed= 0,
                                        exp_bonus=0
        )
    def set_item_bonuses(self):
        checker = Bonus_checker_complete(self.item,self.stage_specific_dict)
        checker.check_inbuilt_bonus()
        checker.check_item_bonus()
    def build(self):
        self.set_item_bonuses()
        return self.item