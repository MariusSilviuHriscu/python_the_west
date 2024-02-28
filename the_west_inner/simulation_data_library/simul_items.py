import math
import typing

from simul_skills import Skills


class Item_update_table():
    """A class to store the update information for an item.

    An instance of this class holds information about whether an item's various stats should be updated, such as skills, workpoints, and regeneration. 
    """
    def __init__(self,
                 skills_updates:bool,
                 work_updates:bool,
                 regen_updates:bool,
                 speed_updates:bool,
                 item_drop_updates:bool,
                 product_drop_updates:bool,
                 exp_bonus_updates:bool,
                 damage_updates:bool):
        """Initializes the update table with the update information.

        Args:
        skills_updates (bool): A flag indicating whether the skills should be updated.
        work_updates (bool): A flag indicating whether the workpoints should be updated.
        regen_updates (bool): A flag indicating whether the regeneration should be updated.
        speed_updates (bool): A flag indicating whether the speed should be updated.
        item_drop_updates (bool): A flag indicating whether the item drop should be updated.
        product_drop_updates (bool): A flag indicating whether the product drop should be updated.
        exp_bonus_updates (bool): A flag indicating whether the experience bonus should be updated.
        damage_updates (bool): A flag indicating whether the damage should be updated.
        """
        self.skills_updates = skills_updates
        self.work_updates = work_updates
        self.regen_updates = regen_updates
        self.speed_updates = speed_updates
        self.item_drop_updates = item_drop_updates
        self.product_drop_updates = product_drop_updates
        self.exp_bonus_updates = exp_bonus_updates
        self.damage_updates = damage_updates

    def __getitem__(self, key):
        """Get the value for a given key in the updates dictionary.

        Args:
        key (str): The key to retrieve the value for.

        Returns:
        The value associated with the given key.
        """
        return self.__dict__[key]

    def __str__(self):
        """Return a string representation of the updates information.

        Returns:
        A string with the form: 'skills updates: X, work updates: Y, regen updates: Z, ...'
        where X, Y, Z, etc. are the values of the various update flags.
        """
        return f'skills updates: {self.skills_updates}, work updates: {self.work_updates}, regen updates: {self.regen_updates}, speed updates: {self.speed_updates}, item drop updates: {self.item_drop_updates}, product drop updates: {self.product_drop_updates}, exp bonus updates: {self.exp_bonus_updates}, damage updates: {self.damage_updates}'


class Item_model():
    """
    The Item_model class is a more complex class that defines a blueprint for a single item in the game. 
    It stores information about the item, such as its name, id, value, status, item set, updates, level,
    and various statistics like workpoints, regeneration, damage, speed, and experience bonus.
    The __repr__ and __str__ methods return a string representation of the instance.
    """
    def __init__(self, 
                 name : str, 
                 item_id : int,
                 value : int,
                 status : Skills,
                 item_set : int, 
                 updates : Item_update_table, 
                 level : int, 
                 item_drop : int, 
                 product_drop : int, 
                 workpoints : int, 
                 regeneration : int, 
                 damage : int, 
                 speed : int,
                 exp_bonus : int, 
                 dropable : bool, 
                 sellable : bool, 
                 actionable : bool, 
                 upgradeable : bool
                 ):
        """
        Constructor method for the Item_model class.
        
        Parameters:
        name (str): The name of the item.
        item_id (int): The id of the item.
        value (int): The value of the item.
        status (int): The status of the item.
        item_set (str): The set the item belongs to.
        updates (Item_update_table): The updates of the item.
        level (int): The level of the item.
        item_drop (int): The amount of item drop.
        product_drop (int): The amount of product drop.
        workpoints (int): The workpoints of the item.
        regeneration (int): The regeneration of the item.
        damage (int): The damage of the item.
        speed (int): The speed of the item.
        dropable (bool): A flag that indicates if the item can be dropped.
        sellable (bool): A flag that indicates if the item can be sold.
        actionable (bool): A flag that indicates if the item can be used.
        upgradeable (bool): A flag that indicates if the item can be upgraded.
        exp_bonus (int): The bonus experience points.
        """
        # Assigning class variables with the parameters
        self.name = name
        self.item_id = item_id
        self.value = value
        self.status = status
        self.item_set = item_set
        self.updates = updates
        self.level = level
        self.item_drop = item_drop
        self.product_drop = product_drop
        self.workpoints = workpoints
        self.regeneration = regeneration
        self.damage = damage
        self.speed = speed
        self.dropable = dropable
        self.sellable = sellable
        self.actionable = actionable
        self.upgradeable = upgradeable
        self.exp_bonus = exp_bonus
    
    def __repr__(self):
        """
        Representation method for the Item_model class.
        """
        return self.__str__()
    
    def __str__(self):
        """
        String representation method for the Item_model class.
        
        Returns:
        (str) : string representation of the Item_model object
        """
        # returning a formatted string of the Item_model object's variables
        return (
            f'name: {self.name}, '
            f'item_id: {self.item_id}, '
            f'value: {self.value}, '
            f'status: {self.status}, '
            f'item_set: {self.item_set}, '
            f'updates: {self.updates}, '
            f'level: {self.level}, '
            f'item_drop: {self.item_drop}, '
            f'product_drop: {self.product_drop}, '
            f'workpoints: {self.workpoints}, '
            f'regeneration: {self.regeneration}, '
            f'damage: {self.damage}, '
            f'speed: {self.speed}, '
            f'dropable: {self.dropable}, '
            f'sellable: {self.sellable}, '
            f'actionable: {self.actionable}, '
            f'upgradeable: {self.upgradeable}, '
            f'exp_bonus: {self.exp_bonus}'
        )
    def has_bonus(self,attribute_key:str) -> bool:
        return self.__dict__[attribute_key] != 0
    def __eq__(self,other:typing.Self) -> bool:
        return self.item_id == other.item_id


    
class Item():
    """
    The Item class represents a specific item that a player has in their inventory.
    The class takes an Item_model and a player as arguments and calculates various statistics for the item based on the player's level and the item's updates attribute,
    using methods like update_skills, update_item_drop, update_workpoints, update_regeneration, update_damage, update_speed, and update_exp_bonus.
    The update_all method is used to recalculate all of the item's statistics.
    """
    def __init__(self,item_model,player_level):
        self.item_model = item_model
        self.player_level = player_level
        self.item_skills = self.update_skills()
        self.item_drop = self.update_item_drop()
        self.workpoints = self.update_workpoints()
        self.product_drop = self.update_product_drop()
        self.regeneration = self.update_regeneration()
        self.damage = self.update_damage()
        self.speed = self.update_speed()
        self.exp_bonus = self.update_exp_bonus()
    def update_all(self):
        self.__init__(self.item_model,self.player_level)
    def update_by_level(self,new_level:int):
        self.player_level = new_level
        self.update_all()
    def update_skills(self):
        if self.item_model.updates.skills_updates == False:
            return self.item_model.status
        else:
            base_stats = self.item_model.status
            return round(base_stats*self.player_level,"ceil")
    def update_item_drop(self):
        if self.item_model.updates.item_drop_updates == False:
            return self.item_model.item_drop
        else:
            base_stats = math.ceil(self.item_model.item_drop*self.player_level)
            return base_stats
    def update_workpoints(self):
        if self.item_model.updates.work_updates == False:
            return self.item_model.workpoints
        else:
            base_stats = math.ceil(self.item_model.workpoints*self.player_level)
            return base_stats
    def update_product_drop(self):
        if self.item_model.updates.product_drop_updates == False:
            return self.item_model.product_drop
        else:
            base_stats = math.ceil(self.item_model.product_drop*self.player_level)
            return base_stats
    def update_regeneration(self):
        if self.item_model.updates.regen_updates == False:
            return self.item_model.regeneration
        else:
            base_stats = math.ceil(self.item_model.regeneration*self.player_level)
            return base_stats
    def update_damage(self):
        if self.item_model.updates.damage_updates == False:
            return self.item_model.damage
        else:
            base_stats = math.ceil(self.item_model.damage*self.player_level)
            return base_stats
    def update_speed(self):
        if self.item_model.updates.speed_updates == False:
            return self.item_model.speed
        else:
            base_stats = math.ceil(self.item_model.speed*self.player_level)
            return base_stats
    def update_exp_bonus(self):
        if self.item_model.updates.exp_bonus_updates == False:
            return self.item_model.exp_bonus
        else:
            base_stats = math.ceil(self.item_model.exp_bonus*self.player_level)
            return base_stats
    @property
    def item_type(self):
        return self.item_model.type
class Produs(Item_model):
    def __init__(self, name: str, 
                 item_id: int,
                 value: int, 
                 status: Skills, 
                 item_set: int, 
                 updates: Item_update_table, 
                 level: int, 
                 item_drop: int, 
                 product_drop: int, 
                 workpoints: int, 
                 regeneration: int, 
                 damage: int, 
                 speed: int, 
                 exp_bonus: int, 
                 dropable: bool, 
                 sellable: bool, 
                 actionable: bool, 
                 upgradeable: bool):
        super().__init__(name,
                        item_id,
                        value,
                        status,
                        item_set,
                        updates,
                        level,
                        item_drop,
                        product_drop,
                        workpoints,
                        regeneration,
                        damage,
                        speed,
                        exp_bonus,
                        dropable,
                        sellable,
                        actionable,
                        upgradeable)
        self.is_mapdrop = False
    @property
    def item_type(self):
        return "produs"

class Weapon_damage_range:
    def __init__(self, min_damage : int , max_damage : int):
        self.min_damage = min_damage
        self.max_damage = max_damage
        self.__radd__ = self.__add__
    def __str__(self):
        
        return f"{{ min_damage : {self.min_damage} , max_damage : {self.max_damage} }}"
    
    def __repr__(self) -> str:
        return f"Weapon_damage_range( {self.__str__()} )"
    def __add__(self,other : int | typing.Self) -> typing.Self:
        if isinstance(other,Weapon_damage_range):
            return Weapon_damage_range(
                min_damage = self.min_damage + other.min_damage,
                max_damage = self.max_damage + other.max_damage
            )
        elif isinstance(other , int):
            return Weapon_damage_range(
                min_damage = self.min_damage + other ,
                max_damage = self.max_damage + other 
            )
        else :
            raise TypeError('Inapropriate type of object added to Weapon_damage_range')
    def average(self) -> int:
        return int( (self.max_damage + self.min_damage) / 2 )
    
class Weapon(Item_model):
    def __init__(self, name: str, 
                 item_id: int,
                 value: int, 
                 status: Skills, 
                 item_set: int, 
                 updates: Item_update_table, 
                 level: int, 
                 item_drop: int, 
                 product_drop: int, 
                 workpoints: int, 
                 regeneration: int, 
                 damage: int, 
                 speed: int, 
                 exp_bonus: int, 
                 dropable: bool, 
                 sellable: bool, 
                 actionable: bool, 
                 upgradeable: bool):
        super().__init__(name,
                        item_id,
                        value,
                        status,
                        item_set,
                        updates,
                        level,
                        item_drop,
                        product_drop,
                        workpoints,
                        regeneration,
                        damage,
                        speed,
                        exp_bonus,
                        dropable,
                        sellable,
                        actionable,
                        upgradeable)
        self.weapon_damage = Weapon_damage_range(
            min_damage = 0,
            max_damage = 0
        )
    @property
    def item_type(self):
        return "weapon"
class Fort_weapon(Item_model):
    def __init__(self, name: str, 
                 item_id: int,
                 value: int, 
                 status: Skills, 
                 item_set: int, 
                 updates: Item_update_table, 
                 level: int, 
                 item_drop: int, 
                 product_drop: int, 
                 workpoints: int, 
                 regeneration: int, 
                 damage: int, 
                 speed: int, 
                 exp_bonus: int, 
                 dropable: bool, 
                 sellable: bool, 
                 actionable: bool, 
                 upgradeable: bool):
        super().__init__(name,
                        item_id,
                        value,
                        status,
                        item_set,
                        updates,
                        level,
                        item_drop,
                        product_drop,
                        workpoints,
                        regeneration,
                        damage,
                        speed,
                        exp_bonus,
                        dropable,
                        sellable,
                        actionable,
                        upgradeable)
    @property
    def item_type(self):
        return "fort_weapon"
class Necklace(Item_model):
    def __init__(self, name: str, 
                 item_id: int,
                 value: int, 
                 status: Skills, 
                 item_set: int, 
                 updates: Item_update_table, 
                 level: int, 
                 item_drop: int, 
                 product_drop: int, 
                 workpoints: int, 
                 regeneration: int, 
                 damage: int, 
                 speed: int, 
                 exp_bonus: int, 
                 dropable: bool, 
                 sellable: bool, 
                 actionable: bool, 
                 upgradeable: bool):
        super().__init__(name,
                        item_id,
                        value,
                        status,
                        item_set,
                        updates,
                        level,
                        item_drop,
                        product_drop,
                        workpoints,
                        regeneration,
                        damage,
                        speed,
                        exp_bonus,
                        dropable,
                        sellable,
                        actionable,
                        upgradeable)
    @property
    def item_type(self):
        return "necklace"

class Clothes(Item_model):
    def __init__(self, name: str, 
                 item_id: int,
                 value: int, 
                 status: Skills, 
                 item_set: int, 
                 updates: Item_update_table, 
                 level: int, 
                 item_drop: int, 
                 product_drop: int, 
                 workpoints: int, 
                 regeneration: int, 
                 damage: int, 
                 speed: int, 
                 exp_bonus: int, 
                 dropable: bool, 
                 sellable: bool, 
                 actionable: bool, 
                 upgradeable: bool):
        super().__init__(name,
                        item_id,
                        value,
                        status,
                        item_set,
                        updates,
                        level,
                        item_drop,
                        product_drop,
                        workpoints,
                        regeneration,
                        damage,
                        speed,
                        exp_bonus,
                        dropable,
                        sellable,
                        actionable,
                        upgradeable)
    @property
    def item_type(self):
        return "clothes"
class Pants(Item_model):
    def __init__(self, name: str, 
                 item_id: int,
                 value: int, 
                 status: Skills, 
                 item_set: int, 
                 updates: Item_update_table, 
                 level: int, 
                 item_drop: int, 
                 product_drop: int, 
                 workpoints: int, 
                 regeneration: int, 
                 damage: int, 
                 speed: int, 
                 exp_bonus: int, 
                 dropable: bool, 
                 sellable: bool, 
                 actionable: bool, 
                 upgradeable: bool):
        super().__init__(name,
                        item_id,
                        value,
                        status,
                        item_set,
                        updates,
                        level,
                        item_drop,
                        product_drop,
                        workpoints,
                        regeneration,
                        damage,
                        speed,
                        exp_bonus,
                        dropable,
                        sellable,
                        actionable,
                        upgradeable)
    @property
    def item_type(self):
        return "pants"

class Boots(Item_model):
    def __init__(self, name: str, 
                 item_id: int,
                 value: int, 
                 status: Skills, 
                 item_set: int, 
                 updates: Item_update_table, 
                 level: int, 
                 item_drop: int, 
                 product_drop: int, 
                 workpoints: int, 
                 regeneration: int, 
                 damage: int, 
                 speed: int, 
                 exp_bonus: int, 
                 dropable: bool, 
                 sellable: bool, 
                 actionable: bool, 
                 upgradeable: bool):
        super().__init__(name,
                        item_id,
                        value,
                        status,
                        item_set,
                        updates,
                        level,
                        item_drop,
                        product_drop,
                        workpoints,
                        regeneration,
                        damage,
                        speed,
                        exp_bonus,
                        dropable,
                        sellable,
                        actionable,
                        upgradeable)
    @property
    def item_type(self):
        return "boots"
class Headgear(Item_model):
    def __init__(self, name: str, 
                 item_id: int,
                 value: int, 
                 status: Skills, 
                 item_set: int, 
                 updates: Item_update_table, 
                 level: int, 
                 item_drop: int, 
                 product_drop: int, 
                 workpoints: int, 
                 regeneration: int, 
                 damage: int, 
                 speed: int, 
                 exp_bonus: int, 
                 dropable: bool, 
                 sellable: bool, 
                 actionable: bool, 
                 upgradeable: bool):
        super().__init__(name,
                        item_id,
                        value,
                        status,
                        item_set,
                        updates,
                        level,
                        item_drop,
                        product_drop,
                        workpoints,
                        regeneration,
                        damage,
                        speed,
                        exp_bonus,
                        dropable,
                        sellable,
                        actionable,
                        upgradeable)
    @property
    def item_type(self):
        return "headgear"
class Belt(Item_model):
    def __init__(self, name: str, 
                 item_id: int,
                 value: int, 
                 status: Skills, 
                 item_set: int, 
                 updates: Item_update_table, 
                 level: int, 
                 item_drop: int, 
                 product_drop: int, 
                 workpoints: int, 
                 regeneration: int, 
                 damage: int, 
                 speed: int, 
                 exp_bonus: int, 
                 dropable: bool, 
                 sellable: bool, 
                 actionable: bool, 
                 upgradeable: bool):
        super().__init__(name,
                        item_id,
                        value,
                        status,
                        item_set,
                        updates,
                        level,
                        item_drop,
                        product_drop,
                        workpoints,
                        regeneration,
                        damage,
                        speed,
                        exp_bonus,
                        dropable,
                        sellable,
                        actionable,
                        upgradeable)
    @property
    def item_type(self):
        return "belt"
class Animal(Item_model):
    def __init__(self, name: str, 
                 item_id: int,
                 value: int, 
                 status: Skills, 
                 item_set: int, 
                 updates: Item_update_table, 
                 level: int, 
                 item_drop: int, 
                 product_drop: int, 
                 workpoints: int, 
                 regeneration: int, 
                 damage: int, 
                 speed: int, 
                 exp_bonus: int, 
                 dropable: bool, 
                 sellable: bool, 
                 actionable: bool, 
                 upgradeable: bool):
        super().__init__(name,
                        item_id,
                        value,
                        status,
                        item_set,
                        updates,
                        level,
                        item_drop,
                        product_drop,
                        workpoints,
                        regeneration,
                        damage,
                        speed,
                        exp_bonus,
                        dropable,
                        sellable,
                        actionable,
                        upgradeable)
    @property
    def item_type(self):
        return "animal"

class Item_model_list():
    def __init__(self,item_model_list:list[typing.Type[Item_model]]):
        self.item_model_list = item_model_list
    def __iter__(self):
        return iter(self.item_model_list)
    def filter_by_bonus(self,attribute_key:str) -> typing.Self:
        return Item_model_list(
            item_model_list= [x for x in self.item_model_list if x.has_bonus( attribute_key= attribute_key) ]
        )
    def __len__(self):
        return len(self.item_model_list)
    def count_item_types(self) -> dict[str,int]:
        item_count_dict = {}
        for item_model in self.item_model_list:
            item_type = item_model.item_type
            if item_model.item_type in item_count_dict:
                item_count_dict[item_type] += 1
            else:
                item_count_dict[item_type] = 1
        return item_count_dict
    def calc_permutations(self) -> int:
        item_dict = self.count_item_types()
        
        return math.prod(item_dict.values())
    def filter_by_player_level(self,player_level:int) -> typing.Self:
        return Item_model_list(
            item_model_list = [x for x in self.item_model_list if x.level <= player_level]
        )
    def filter_by_set_keys(self,*sets:list[str]|str) -> typing.Self:
        return Item_model_list(
            item_model_list= [x for x in self.item_model_list if x in sets]
        )
    def union(self,other:typing.Self) -> typing.Self:
        return Item_model_list(
            item_model_list= list(set(self.item_model_list + other.item_model_list))
        )
    def filter_by_item_id_list(self,sets:list[int]|int) -> typing.Self:
        return Item_model_list(
            item_model_list = [x for x in self.item_model_list if x.item_id in sets]
        )
    def filter_mapdrop_items(self) -> typing.Self:    
        return Item_model_list(
            item_model_list = [x for x in self.item_model_list if not (x.item_type == 'produs' and x.is_mapdrop) ]
        ) 
    def get_model_by_id(self,item_id:int):
        if item_id is None:
            return None
        for item_model in self.item_model_list:
            if item_model.item_id == item_id:
                return item_model
        raise Exception(f"Item model id not found {item_id} in {[x.item_id for x in self.item_model_list]}")
    def get_item_dict(self) -> dict[str, Item_model]:
        item_dict = {}
        # Create a set of unique item types
        item_types = set(item_model.item_type for item_model in self.item_model_list)
        
        # Iterate over each item type and filter the item_model_list for that type
        for item_type in item_types:
            filtered_items = [item_model for item_model in self.item_model_list if item_model.item_type == item_type]
            # Add the filtered list to the dictionary with the item_type as the key
            item_dict[item_type] = filtered_items
        
        return item_dict

class Item_list():
    def __init__(self,items:dict[int:dict[typing.Literal["item","item_model"]:Item|typing.Type[Item_model]]],player_level:int):
        self.items = items
        self.player_level = player_level
    def __iter__(self):
        return iter(
            [x['item'] for x in self.items.values()]
            )
    def eliminate_by_id(self,*ids) -> typing.Self:
        return Item_list(
                    items = {item_id:value for item_id,value in self.items.items() if value not in ids},
                    player_level= self.player_level
                    )
    def filter_by_id_list(self,id_list:list[int]) -> typing.Self:
        return Item_list(
                        items = {item_id:item_dict for item_id,item_dict in self.items if item_id in id_list},
                        player_level = self.player_level
                        )
    def get_items(self):
        return [x['item'] for x in self.items.values()]
    def update_level(self,new_level:int):
        self.player_level = new_level
        for item_instance in self.items.values():
            item_instance['item'].update()
    def __getitem__(self,item_id:int):
        return self.items.get(item_id)['item']
    def get_bonus_by_name(self, bonus_name:str) -> int:
        return sum(
            [getattr( x , bonus_name ) for x in self.get_items()]
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

def create_item_list_from_model(item_model_list : Item_model_list,player_level : int):
    items_dict = {x.item_id : {"item":Item( item_model = x , player_level = player_level),
                         "item_model" : x
                         }
                    for x in item_model_list}
    return Item_list(items= items_dict ,player_level= player_level)