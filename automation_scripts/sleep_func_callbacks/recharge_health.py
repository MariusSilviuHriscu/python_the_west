


from the_west_inner.bag import Bag
from the_west_inner.consumable import Consumable_handler
from the_west_inner.items import Items
from the_west_inner.player_data import Player_data

def select_usable(usable_list : list[int],bag : Bag ) -> int:
    
    for usable in usable_list:
        
        if bag[usable] > 0 :
            return usable

def recharge_health(usable_list : list[int],bag : Bag ,consumable_manager : Consumable_handler):
    
    usable = select_usable(usable_list=usable_list , bag= bag)
    
    consumable_manager.use_consumable(consumable_id = usable)

def recharge_health_script(player_data : Player_data ,
                    usable_list : list[int],
                    min_percent_hp : int ,
                    bag : Bag ,
                    consumable_manager : Consumable_handler):
    
    if player_data.hp / player_data.hp_max * 100 > min_percent_hp:
        
        return 
    
    recharge_health(
        usable_list= usable_list ,
        bag= bag,
        consumable_manager= consumable_manager
    )
    
    