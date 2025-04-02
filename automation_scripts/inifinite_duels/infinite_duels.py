


import time
from the_west_inner.consumable import Consumable_handler
from the_west_inner.duels import (NpcDuelManager , 
                                  DuelResultData ,
                                  NpcDuelException)
from the_west_inner.equipment import Equipment_manager, Equipment
from the_west_inner.player_data import Player_data
from the_west_inner.requests_handler import requests_handler


class InfiniteDuelsSettings:
    
    def __init__(self ,
                 equipment_recharge : Equipment,
                 motivation_recharge_id : int,
                 motivation_recharge_amount : int,
                 health_recharge_threshold : int
                 ):
        
        self.equipment_recharge = equipment_recharge
        self.motivation_recharge_id = motivation_recharge_id
        self.motivation_recharge_amount = motivation_recharge_amount
        self.health_recharge_threshold = health_recharge_threshold
        
    
    def should_recharge_motivation(self , current_motivation : int) -> bool:
        print(f'current_motivation is {current_motivation}')
        return current_motivation <= 100 - self.motivation_recharge_amount
    
    def should_recharge_health(self , current_health : int , max_health : int) -> bool:
        print(f'current health {current_health}')
        print(f'max hp {max_health}')
        return current_health <= self.health_recharge_threshold * max_health
    
    def should_recharge_energy(self , current_energy : int) -> bool:
        return current_energy < 5
    
    

class InfiniteDuelsManager:
    
    def __init__(self ,
                 
                 handler : requests_handler ,
                 equipment_manager : Equipment_manager ,
                 consumable_handler : Consumable_handler ,
                 player_data : Player_data
                 
                 ):
        
        self.handler = handler
        self.equipment_manager = equipment_manager
        self.consumable_handler = consumable_handler
        self.player_data = player_data
        
        self.duel_manager = NpcDuelManager(
                        handler= handler,
                        equipment_manager= equipment_manager,
                        player_data= player_data
                        )
        
        self.duel_loop_generator = self.duel_manager.cycle_duels()
    
    def recharge_health_and_energy(self , settings : InfiniteDuelsSettings):
        hp , max_hp = self.player_data.hp , self.player_data.hp_max
        with self.equipment_manager.temporary_equipment(new_equipment= settings.equipment_recharge,
                                                        handler= self.handler):
            self.player_data.update_all(handler= self.handler)
            while (settings.should_recharge_health(self.player_data.hp , max_hp) 
                    or 
                    settings.should_recharge_energy(self.player_data.energy)
                    ):
                
                print('Should recharge hp')
                
                
                time.sleep(60)
                
                self.player_data.update_all(handler= self.handler)
            
    def recharge_motivation(self , settings : InfiniteDuelsSettings):
        
        if settings.should_recharge_motivation(self.duel_manager.npc_list._npc_duel_motivation*100):
            
            print('Should recharge mot')
            
            with self.equipment_manager.temporary_equipment(new_equipment= settings.equipment_recharge,
                                                        handler= self.handler):
                
                self.consumable_handler.use_consumable(consumable_id= settings.motivation_recharge_id)
                time.sleep(20)
        
    
    def advance_duel(self , settings  : InfiniteDuelsSettings) -> DuelResultData:
        
        result = next(self.duel_loop_generator)
        print(result)
        self.recharge_health_and_energy(settings= settings)
        time.sleep(10)
        self.recharge_motivation(settings= settings)
        time.sleep(10)
        
        return result
    
    def loop_duels(self , settings : InfiniteDuelsSettings , target_lvl : int) -> list[DuelResultData]:
        results = []
        while self.duel_manager.npc_list._difficulty < target_lvl:
            try:
                result = self.advance_duel(settings= settings)
                results.append(result)
            except NpcDuelException :
                pass
            except StopIteration:
                pass
            except Exception as e:
                raise e
        
        return results
        
        
        