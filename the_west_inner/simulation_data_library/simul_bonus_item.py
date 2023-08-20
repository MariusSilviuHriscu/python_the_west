class Character_attribute_bonus_chain():
    def __init__(self,bonus_dict,item,next_chain=None):
        self.bonus_dict = bonus_dict
        self.next_chain = next_chain
        self.item = item
    def add_bonus_to_item(self,value,attribute_name):
        self.item.status[attribute_name] += value
        if 'key' in self.bonus_dict and self.bonus_dict['key'] == 'level':
            self.item.updates.skills_updates = True
    def check_bonus(self):
        if self.bonus_dict['type'] == 'character' and self.bonus_dict['bonus']['type']=='attribute':
            self.add_bonus_to_item(self.bonus_dict['bonus']['value'],self.bonus_dict['bonus']['name'])
        elif self.next_chain is not None:
            self.next_chain.item = self.item
            self.next_chain.bonus_dict = self.bonus_dict
            #print(self.next_chain.bonus_dict,self.next_chain.item)
            self.next_chain.check_bonus()
class Character_skill_bonus_chain():
    def __init__(self,bonus_dict,item,next_chain=None):
        self.bonus_dict = bonus_dict
        self.next_chain = next_chain
        self.item = item
    def add_bonus_to_item(self,value,skill_name):
        self.item.status[skill_name] += value
        if 'key' in self.bonus_dict and self.bonus_dict['key'] == 'level':
            self.item.updates.skills_updates = True
    def check_bonus(self):
        #print(self.bonus_dict)
        if self.bonus_dict['type'] == 'character' and self.bonus_dict['bonus']['type']=='skill' :
            self.add_bonus_to_item(self.bonus_dict['bonus']['value'],self.bonus_dict['bonus']['name'])
        elif self.next_chain is not None:
            self.next_chain.item = self.item
            self.next_chain.bonus_dict = self.bonus_dict
            self.next_chain.check_bonus()
class Character_item_drop_bonus_chain():
    def __init__(self,bonus_dict,item,next_chain=None):
        self.bonus_dict = bonus_dict
        self.next_chain = next_chain
        self.item = item
    def add_bonus_to_item(self,value):
        self.item.item_drop += value
        if 'key' in self.bonus_dict and self.bonus_dict['key'] == 'level':
            self.item.updates.item_drop_updates = True
    def check_bonus(self):
        if self.bonus_dict['type'] == 'luck':
            self.add_bonus_to_item(self.bonus_dict['value'])
        elif self.next_chain is not None:
            self.next_chain.item = self.item
            self.next_chain.bonus_dict = self.bonus_dict
            self.next_chain.check_bonus()
class Character_product_drop_bonus_chain():
    def __init__(self,bonus_dict,item,next_chain=None):
        self.bonus_dict = bonus_dict
        self.next_chain = next_chain
        self.item = item
    def add_bonus_to_item(self,value):
        self.item.product_drop += value
        if 'key' in self.bonus_dict and self.bonus_dict['key'] == 'level':
            self.item.updates.product_drop_updates = True
    def check_bonus(self):
        if self.bonus_dict['type'] == 'drop':
            self.add_bonus_to_item(self.bonus_dict['value'])
        elif self.next_chain is not None:
            self.next_chain.item = self.item
            self.next_chain.bonus_dict = self.bonus_dict
            self.next_chain.check_bonus()
class Character_exp_bonus_chain():
    def __init__(self,bonus_dict,item,next_chain=None):
        self.bonus_dict = bonus_dict
        self.next_chain = next_chain
        self.item = item
    def add_bonus_to_item(self,value):
        self.item.exp_bonus += value
        if 'key' in self.bonus_dict and self.bonus_dict['key'] == 'level':
            self.item.updates.exp_bonus_updates = True
    def check_bonus(self):
        if self.bonus_dict['type'] == 'drop':
            self.add_bonus_to_item(self.bonus_dict['value'])
        elif self.next_chain is not None:
            self.next_chain.item = self.item
            self.next_chain.bonus_dict = self.bonus_dict
            self.next_chain.check_bonus()
class Character_workpoints_bonus_chain():
    def __init__(self,bonus_dict,item,next_chain=None):
        self.bonus_dict = bonus_dict
        self.next_chain = next_chain
        self.item = item
    def add_bonus_to_item(self,value):
        self.item.workpoints += value
        if 'key' in self.bonus_dict and self.bonus_dict['key'] == 'level':
            self.item.updates.work_updates = True
    def check_bonus(self):
        if self.bonus_dict['type'] == 'job' and 'job' in  self.bonus_dict and self.bonus_dict['job'] == 'all':
            self.add_bonus_to_item(self.bonus_dict['value'])
        elif self.next_chain is not None:
            self.next_chain.item = self.item
            self.next_chain.bonus_dict = self.bonus_dict
            self.next_chain.check_bonus()
class Character_bonus_speed_bonus_chain():
    def __init__(self,bonus_dict,item,next_chain=None):
        self.bonus_dict = bonus_dict
        self.next_chain = next_chain
        self.item = item
    def add_bonus_to_item(self,value):
        self.item.speed += value
        if 'key' in self.bonus_dict and self.bonus_dict['key'] == 'level':
            self.item.updates.speed_updates = True
    def check_bonus(self):
        if self.bonus_dict['type'] == 'speed':
            self.add_bonus_to_item(self.bonus_dict['value'])
        elif self.next_chain is not None:
            self.next_chain.item = self.item
            self.next_chain.bonus_dict = self.bonus_dict
            self.next_chain.check_bonus()
class Character_bonus_regen_bonus_chain():
    def __init__(self,bonus_dict,item,next_chain=None):
        self.bonus_dict = bonus_dict
        self.next_chain = next_chain
        self.item = item
    def add_bonus_to_item(self,value):
        self.item.regeneration += value
        if 'key' in self.bonus_dict and self.bonus_dict['key'] == 'level':
            self.item.updates.regen_updates = True
    def check_bonus(self):
        if self.bonus_dict['type'] == 'regen':
            self.add_bonus_to_item(self.bonus_dict['value'])
        elif self.next_chain is not None:
            self.next_chain.item = self.item
            self.next_chain.bonus_dict = self.bonus_dict
            self.next_chain.check_bonus()


def create_chain():
    character_attribute_checker = Character_attribute_bonus_chain(None,None)
    character_skill_checker = Character_skill_bonus_chain(None,None)
    character_item_drop_checker = Character_item_drop_bonus_chain(None,None)
    character_product_drop_checker = Character_product_drop_bonus_chain(None,None)
    character_exp_checker = Character_exp_bonus_chain(None,None)
    character_workpoints_checker = Character_workpoints_bonus_chain(None,None)
    character_bonus_speed_checker = Character_bonus_speed_bonus_chain(None,None)
    character_bonus_regen_checker = Character_bonus_regen_bonus_chain(None,None)
    character_attribute_checker.next_chain = character_skill_checker
    character_skill_checker.next_chain = character_item_drop_checker
    character_item_drop_checker.next_chain = character_product_drop_checker
    character_product_drop_checker.next_chain = character_exp_checker
    character_exp_checker.next_chain = character_workpoints_checker
    character_workpoints_checker.next_chain = character_bonus_speed_checker
    character_bonus_speed_checker.next_chain = character_bonus_regen_checker
    character_bonus_regen_checker.next_chain = None
    return character_attribute_checker


class Bonus_checker_complete():
    def __init__(self,item,bonus_dict):
        self.item = item
        self.bonus_dict = bonus_dict
    def check_inbuilt_bonus(self):
        for attribute in self.bonus_dict['attributes']:
            self.item.status[attribute] += int(self.bonus_dict['attributes'][attribute])
        for skill in self.bonus_dict['skills']:
            self.item.status[skill] += int(self.bonus_dict['skills'][skill])
    def check_item_bonus(self):
        chain = create_chain()
        for item_bonus in self.bonus_dict['item']:
            chain.item = self.item
            chain.bonus_dict = item_bonus
            chain.check_bonus()