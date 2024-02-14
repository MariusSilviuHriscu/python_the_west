from the_west_inner.quest_requirements import Quest_requirement_duel_npc
from the_west_inner.requests_handler import requests_handler
from the_west_inner.equipment import Equipment,Equipment_manager
from the_west_inner.player_data import Player_data
from the_west_inner.duels import NpcDuelManager

class NpcDuelQuestSolver():
    def __init__(self ,
                 quest_requirement : Quest_requirement_duel_npc,
                 handler : requests_handler,
                 equipment_manager : Equipment_manager,
                 player_data : Player_data,
                 
                 duel_equipment : Equipment = None
                 ):
        
        self.quest_requirement = quest_requirement
        self.handler = handler
        self.equipment_manager = equipment_manager
        self.player_data = player_data
        self.duel_equipment = duel_equipment
    
    def solve(self) -> bool :
        
        npc_duel_manager = NpcDuelManager(
            handler = self.handler,
            equipment_manager = self.equipment_manager ,
            player_data = self.player_data
        )
        npc_duel_manager.set_duel_equipment(duel_set=self.duel_equipment)
        
        data = npc_duel_manager.duel_smallest_aim_npc()
        
        return True