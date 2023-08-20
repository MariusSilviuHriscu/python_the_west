import copy

from ..bag import Bag
from ..items import Items
from ..equipment import Equipment
from ..item_set_general import Item_sets

from simul_items import Item_model,Item_update_table
from simul_item_builder import Item_builder,Item_set_stage_builder,Item_set_item_model
from simul_sets import Item_set
from simul_skills import Skills

def get_simul_items(bag:Bag,current_equipment:Equipment,items:Items) -> list[Item_model]:
    simul_bag = copy.deepcopy(bag)
    for equipped_item in current_equipment:
        simul_bag.add_item(
            item_id = equipped_item[1]
            )
    return [
        Item_builder(
            item_specific_dict = items.get_item(item_id= x )
        ).build_all() 
        for x in simul_bag.item_dict]
def null_simul_set_instance() -> Item_set_item_model:
    update_table = Item_update_table(*[False for _ in range(8)])
    return Item_set_item_model(
                            updates = update_table,
                            status = Skills.null_skill(),
                            item_drop = 0,
                            product_drop = 0 ,
                            workpoints = 0 ,
                            regeneration = 0 ,
                            damage = 0,
                            speed = 0,
                            exp_bonus = 0
                            )
def get_simul_set_instance(sets:Item_sets) -> Item_set:
    for set_name,set in sets.set_list.items():
        yield Item_set(
            name = set.name,
            set_id= set.key,
            item_list= set.list_items,
            bonuses_dict_by_number = {
                i :Item_set_stage_builder( x ).build()
                                                            for i,x in set.bonus_dict.items()
                } if type(set.bonus_dict) != list else null_simul_set_instance())
def get_simul_sets(sets:Item_sets) ->list[Item_set]:
    return list(
        get_simul_set_instance(sets)
    )