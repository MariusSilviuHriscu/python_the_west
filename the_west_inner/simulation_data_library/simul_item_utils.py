import typing

from simul_items import Item_model
from simul_sets import Item_set


def get_sets_by_value_string(value_string:str,set_list:list[Item_set]):
    for set in set_list:
        if sum([x.__dict__[value_string] for x in set.bonuses_dict_by_number.values()]) != 0:
            yield set

def get_bag_items_by_generator_set(set_generator:typing.Generator[Item_set],bag:list[Item_model]) -> typing.Generator[Item_model]:
    for item_set in set_generator:
        for item_model in bag:
            if item_model.item_set == item_set.set_id:
                yield item_model

def get_bag_items_by_value_string(value_string:str,bag:list[Item_model]):
    for item_model in bag:
        if item_model.__dict__[value_string] != 0:
            yield item_model

def get_items_by_value_string(value_string:str,bag:list[Item_model],set_list:list[Item_set]):
        
    item_set_generator = get_bag_items_by_generator_set(
                        set_generator= get_sets_by_value_string(
                                                    value_string= value_string,
                                                    set_list=set_list
                                                    ),
                        bag= bag
    )
    
    item_generator = get_bag_items_by_value_string(
                                                value_string= value_string,
                                                bag= bag
                                                )
    
    return list(item_set_generator)+ list(item_generator)
    