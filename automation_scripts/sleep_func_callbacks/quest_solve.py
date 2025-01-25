from the_west_inner.game_classes import Game_classes
from copy import deepcopy

from the_west_inner.requests_handler import requests_handler

def solve_christmas_repeatable_quest(handler : requests_handler , game_classes: Game_classes):
    
    handler = game_classes.handler
    if game_classes.bag[709000] == 0:
        print(f'Could not play for {game_classes.player_data.name} because we do not have enough turkeys')
        return False
    handler.post(
        window= 'quest',
        action= 'accept_quest',
        payload = {'quest_id' : '2416'},
        use_h= True
    )
    
    weapon_id = deepcopy(game_classes.equipment_manager.current_equipment.right_arm_item_id)
    if game_classes.work_manager.task_queue.sleep_task_in_queue():
        
        return False
        
    game_classes.equipment_manager.unequip_item(item_id = weapon_id,handler = handler)
    
    response = handler.post(
        window= 'quest',
        action= 'finish_quest',
        payload = {'quest_id' : 2416,'reward_option_id': 0},
        use_h= True
    )
    
    game_classes.equipment_manager.equip_item(item_id=weapon_id , handler= handler)
    
    if response.get('error'):
        
        return False
    
    game_classes.bag.update_inventory(handler = handler)
    
    result = game_classes.consumable_handler.open_box(
        box_id= 50009000
    )
    game_classes.bag.update_inventory(handler = handler)
    
    item_id =  next(iter(result.keys()))
    
    result_final = game_classes.consumable_handler.open_box(
        box_id= item_id
    )
    
    for item_id in result_final:
        print(f'We got {game_classes.items.find_item(item_id=item_id).get("name")}')
    
    return True
    