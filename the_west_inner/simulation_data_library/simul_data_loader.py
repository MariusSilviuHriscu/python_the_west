

from the_west_inner.game_classes import Game_classes
from the_west_inner.item_set_general import get_item_sets

from the_west_inner.simulation_data_library.simul_items import Item_model_list,create_item_list_from_model
from the_west_inner.simulation_data_library.simul_equipment import Equipment_simul
from the_west_inner.simulation_data_library.simul_sets import Item_set_list
from the_west_inner.simulation_data_library.load_items_script import get_simul_items,get_simul_sets
from the_west_inner.simulation_data_library.simul_equipment import _game_data_to_current_equipment


class Simulation_data_loader():
    def __init__(self,game_data: Game_classes):
        
        self.game_data = game_data

    def assemble_item_list_from_game_data(self):
        current_equipment = self.game_data.equipment_manager.current_equipment
        item_list = create_item_list_from_model(
                                        item_model_list = get_simul_items(
                                                                        bag = self.game_data.bag,
                                                                        current_equipment = current_equipment,
                                                                        items = self.game_data.items),
                                        player_level= self.game_data.player_data.level
                                        )
        return item_list

    def assemble_item_model_list_from_game_data(self) -> Item_model_list:
        current_equipment = self.game_data.equipment_manager.current_equipment
        list_of_item_models = get_simul_items(
                                        bag = self.game_data.bag,
                                        current_equipment = current_equipment,
                                        items = self.game_data.items
                                        )
        return Item_model_list(item_model_list = list_of_item_models)
    
    def _request_set_data(self):
        
        return get_item_sets(requests_handler = self.game_data.handler)
    
    def assemble_item_set_model_list_from_game_data(self) -> Item_set_list:
        
        sets = get_simul_sets(
                        sets= self._request_set_data()
                        )
        return Item_set_list(sets)
    def assemble_simul_equipment_from_game_data(self) -> Equipment_simul:
        
        return _game_data_to_current_equipment(game_data=self.game_data)