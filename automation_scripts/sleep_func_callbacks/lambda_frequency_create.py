import typing
from the_west_inner.game_classes import Game_classes


def make_check_health_funct(health_percentage : float , game_classes : Game_classes) -> typing.Callable[[],bool]:
    
    def check_health() -> bool:
        
        game_classes.player_data.update_character_variables(
                                                            handler = game_classes.handler
                                                            )
        
        return game_classes.player_data.hp * 1.0 / game_classes.player_data.hp_max < health_percentage

    return check_health

def make_check_inventory_item_func(item_id : int,item_number : int , game_classes : Game_classes):
    
    def check_inventory_item() -> bool:
        
        return  game_classes.bag[item_id] >= item_number
    
    return check_inventory_item
