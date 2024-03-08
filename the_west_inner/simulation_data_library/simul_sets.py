import typing

from simul_items import Item_model,Item,Item_update_table,Item_list
from simul_skills import Skills

class Item_set_item_model(Item_model):
    """
    Item_set_item_model represents a stage of an item set without taking into account the player's level. 
    
    It includes various attributes such as item_drop, product_drop, workpoints, regeneration, damage, speed, and exp_bonus.
    These attributes can be modified through an updates table, which is passed to the constructor.
    The status attribute is a Skills object that represents the status bonuses that the item provides to the player.
    The name, item_id, and value attributes are inherited from the Item_model class and are not used in the context of item sets.
    The dropable, sellable, actionable, and upgradeable attributes are set to False since item sets are not meant to be sold, used, or upgraded individually. 
    Instead, the bonuses provided by the set are unlocked as more items from the set are equipped by the player.
    """
    def __init__(self,
                 updates:Item_update_table,
                 status:Skills,
                 item_drop:int,
                 product_drop:int,
                 workpoints:int,
                 regeneration:int,
                 damage:int,
                 speed:int,
                 exp_bonus:int
                 ):
        super().__init__(name='',
                         item_id=0,
                         value=0,
                         status=status,
                         item_set = '',
                         updates=updates,
                         level=0,
                         item_drop=item_drop,
                         product_drop=product_drop,
                         workpoints=workpoints,
                         regeneration=regeneration,
                         damage=damage,
                         speed=speed,
                         exp_bonus=exp_bonus,
                         dropable=False,
                         sellable=False,
                         actionable=False,
                         upgradeable=False
                         )
        
class Item_set_item(Item):
    """
    Item_set_item represents the actual bonuses given by an item set, taking into account the player's level. 
    
    It takes an Item_set_item_model object as well as the player's level as input.
    The player_level parameter is used to adjust the attribute values of the Item_set_item_model based on the player's level. 
    This ensures that the bonuses provided by the item set are appropriate for the player's current level.
    The Item_set_item object is created by passing the adjusted Item_set_item_model object to the Item constructor. 
    The Item class is a parent class of Item_set_item and represents an item in general.
    The Item_set_item object inherits all the attributes and methods of the Item class, as well as the modified attributes of the Item_set_item_model.
    Therefore, Item_set_item provides a convenient way to represent the bonuses provided by an item set at a specific player level.
    """
    def __init__(self, item_set_item_model:Item_set_item_model, player_level:int):
        super().__init__(item_model = item_set_item_model,
                         player_level=player_level
                         )


class Item_set():
    def __init__(self,name:str,set_id:str,item_list:list[int],bonuses_dict_by_number:dict[int:Item_set_item]):
        self.name = name
        self.set_id = set_id
        self.item_list = item_list
        self.bonuses_dict_by_number = bonuses_dict_by_number
    def return_bonuses(self,number:int|str) -> Item_set_item :
        if type(number) == int:
            number = str(number)
        return self.bonuses_dict_by_number[number]
    def yield_bonuses(self,number:int|str) -> typing.Generator[Item_set_item,None,None]:
        if type(number) == int:
            number = str(number)
        for set_number,bonus in self.bonuses_dict_by_number.items():
            if set_number == number:
                yield bonus
                return
            yield bonus
    def return_item_set_item(self,number:int|str,player_level:int) -> Item_set_item:
        return Item_set_item(
            item_set_item_model= self.return_bonuses(number=number),
            player_level= player_level
        )
    def has_bonus(self,attribute_key:str) -> bool:
        if  type(self.bonuses_dict_by_number) == Item_set_item_model:
            return False
        for set_stage in self.bonuses_dict_by_number.values():
            if set_stage.__dict__[attribute_key] != 0:
                return True
        return False

class Item_set_list():
    def __init__(self,set_list:list[Item_set]):
        self.set_list = set_list
    def __iter__(self):
        return iter(self.set_list)
    def filter_by_bonus(self,attribute_key:str) -> typing.Self:
        return Item_set_list(
            set_list = [x for x in self.set_list if x.has_bonus(attribute_key = attribute_key)]
        )
    def get(self,key:str):
        for item_set in self.set_list:
            if key == item_set.set_id:
                return item_set
        raise Exception(f"Could not find the desired set! {key}")
    def filter_by_name(self,*key_list:str)-> typing.Self:
        set_list = []
        for key in key_list:
            set_list += [x for x in self.set_list if x.set_id == key]
        return Item_set_list(
            set_list= set_list
        )
    def return_set_key_list(self) ->list[str]:
        return [x.set_id for x in self.set_list]

class Item_set_equipment_list():
    def __init__(self,equipment_item_list:list[Item_set_item],player_level:int):
        self.equipment_item_list = equipment_item_list
        self.player_level = player_level
    def __iter__(self) :
        return iter(self.equipment_item_list)
    def get_sets(self):
        return [x for x in self.equipment_item_list]
    def update_level(self,new_level:int):
        self.player_level = new_level
        for set_bonus_instance in self.equipment_item_list.values():
            set_bonus_instance.update()
    def get_bonus_by_name(self,bonus_name:str) -> int:
        return sum(
            [getattr( x , bonus_name ) for x in self.get_sets()]
        )
    @property
    def item_drop(self):
        return self.get_bonus_by_name("item_drop")
    @property
    def workpoints(self):
        return self.get_bonus_by_name("workpoints")
    @property
    def product_drop(self):
        return self.get_bonus_by_name("product_drop")
    @property
    def regeneration(self):
        return self.get_bonus_by_name("regeneration")
    @property
    def damage(self):   
        return self.get_bonus_by_name("damage")
    @property
    def speed(self):
        return self.get_bonus_by_name("speed")
    @property
    def exp_bonus(self):
        return self.get_bonus_by_name("exp_bonus")
    @property
    def status(self):
        skills = Skills.null_skill()
        for x in self.get_sets():
            skills += x.item_skills
        return skills

def create_set_instance_list(item_set_list:list[Item_set],number_set_dict:dict[str:int],player_level:int) -> Item_set_equipment_list:
    item_set_list = Item_set_list(
                                set_list = item_set_list
                                )
    set_instance_dict = { set_key : Item_set_item(
                                        item_set_item_model = item_set_list.get(set_key).return_bonuses(number=item_number),
                                        player_level= player_level
                                    )
                         for set_key , item_number in number_set_dict.items()
    }
    
    return Item_set_equipment_list(equipment_item_list = list(set_instance_dict.values()) ,player_level= player_level)

def create_set_instance_list(item_set_list:Item_set_list,number_set_dict:dict[str:int],player_level:int) -> Item_set_equipment_list:
    item_set_list = Item_set_list(
                                set_list = item_set_list
                                )
    set_instance_list = []
    
    for set_key, item_number in number_set_dict.items():
        for return_value in item_set_list.get(set_key).yield_bonuses(number=item_number):
            set_instance_list.append(
                                    Item_set_item(
                                        item_set_item_model = return_value,
                                        player_level= player_level
                                    ))
    return Item_set_equipment_list(equipment_item_list = set_instance_list ,player_level= player_level)