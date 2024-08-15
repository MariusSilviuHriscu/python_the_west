import typing
from the_west_inner.movement import character_movement
from the_west_inner.movement_manager import MovementManager
from the_west_inner.player_data import Player_data
from the_west_inner.simulation_data_library.simul_work_cycles.work_cycle_simul_data import WorkCycleSimul,WorkCycleJobSimul
from the_west_inner.work_job_data import WorkData

SIMUL_COOLDOWN_DURATION = 600

class SimulUsableCooldown():
    
    def __init__(self , last_use: int|None = None ):
        
        self.last_use = last_use
    
    def can_use_usable(self , current_time : int ) -> bool:
        if self.last_use is None:
            return True
        return current_time >= self.last_use + SIMUL_COOLDOWN_DURATION
    
    def used_usable(self, time_stamp : int):
        self.last_use = time_stamp
    
    def get_required_time(self , current_time : int) -> int:
        
        if self.last_use is None:
            return 0
        
        return max(0,self.last_use + SIMUL_COOLDOWN_DURATION - current_time)
    
class SimulUsableItem:
    
    def __init__(self, 
                 motivation_recharge : int ,
                 energy_recharge_percent : float):
        self.motivation_recharge = motivation_recharge
        self.energy_recharge_percent = energy_recharge_percent

class SimulationLocationData:
    def __init__(self, x : int, y : int ,exp : int , motivation : int = 100 ):
        
        self.x = x
        self.y = y
        self.exp = exp
        self.motivation = motivation

    @staticmethod
    def load_from_work_cycle_job_simul(work_cycle_job_simul : WorkCycleJobSimul, work_time : int) -> typing.Self:
        
        work_data : WorkData = work_cycle_job_simul.job_data.timed_work_data.get(work_time , None)
        if work_data is None :
            raise Exception('Could not find exp')
        
        
        
        return SimulationLocationData(
            x = work_cycle_job_simul.map_job_location.job_x,
            y = work_cycle_job_simul.map_job_location.job_y,
            exp= work_data.xp if not work_cycle_job_simul.map_job_location.is_silver else work_data.get_silver().xp
        )
    
    def modify_motivation(self, ammount : int):
        
        self.motivation += ammount
        
        if self.motivation > 100:
            self.motivation = 100
        if self.motivation < 0:
            self.motivation = 0
    
    def work_one_job(self) -> int:
        self.modify_motivation(ammount= -1)
        return self.exp
    
    
class WorkCycleSimulation:
    
    def __init__(self,
                 player_data : Player_data ,
                 energy : int ,
                 work_time : int ,
                 work_cycle_simul : WorkCycleSimul ,
                 energy_usable : SimulUsableItem | None = None ,
                 motivation_usable : SimulUsableItem | None = None 
                 ):
        self.position =character_movement(x= 0 , 
                                                    y = 0 ,
                                                    game_travel_speed= player_data.game_data.game_travel_speed ,
                                                    character_speed= player_data.character_movement
                                                    )
        self.energy = energy
        self.max_energy = energy
        if not work_cycle_simul.is_valid_cycle():
            raise ValueError('Invalid work cycle!')
        
        
        
        self.simul_location_data : list[SimulationLocationData] = [SimulationLocationData.load_from_work_cycle_job_simul(
                                                                       work_cycle_job_simul= x , 
                                                                       work_time= work_time 
                                                                       ) for x in work_cycle_simul.work_data_list]
        self.energy_usable = energy_usable
        self.motivation_usable = motivation_usable
        
        self.cooldown : SimulUsableCooldown = SimulUsableCooldown()
        
        self.elapsed_time : int = 0
        self.exp_gained : int = 0
    def recharge_energy(self , energy : float):
        
        self.energy += int(self.max_energy * energy)
    
    def recharge_motivation(self , motivation : int):
        
        for location_data in self.simul_location_data:
            
            location_data.modify_motivation(ammount = motivation)
    
    def _use_consumable(self , consumable : SimulUsableItem):
        self.recharge_energy(energy= consumable.energy_recharge_percent)
        self.recharge_motivation(motivation = consumable.motivation_recharge)
        self.cooldown.used_usable(time_stamp = self.elapsed_time)
    
    def use_energy_consumable(self ) -> bool:
        
        if self.energy_usable is None:
            return False
        
        if self.cooldown.get_required_time(current_time = self.elapsed_time) > 0:
            
            self.elapsed_time += self.cooldown.get_required_time(current_time = self.elapsed_time)
        
        self._use_consumable(consumable=self.energy_usable)

        return True
    
    def use_motivation_consumable(self ) -> bool:
        
        if self.motivation_usable is None:
            return False
        
        if self.cooldown.get_required_time(current_time = self.elapsed_time) > 0:
            
            self.elapsed_time += self.cooldown.get_required_time(current_time = self.elapsed_time)
        
        self._use_consumable(consumable=self.motivation_usable)
        return True
    
    
    def go_to_location(self, location : SimulationLocationData):
        

        move_x , move_y = (location.x,
                            location.y)
        if self.position.character_position == (0,0):
            self.position.character_position = (move_x,
                                                 move_y)
            return
        
        travel_time = self.position.calculate_distance_to(final_position = (move_x, move_y))
        self.elapsed_time += travel_time
        self.position.x , self.position.y = (move_x,
                                            move_y)
    
    def can_afford_motivation_wise(self) -> bool:
        
        return any([x.motivation > 75 for x in self.simul_location_data])
    
    def can_afford_energy_wise(self) -> bool:
        
        return self.energy > 0
    
    def can_continue(self):
        return self.can_afford_energy_wise() and self.can_afford_motivation_wise()
    
    def work(self , location : SimulationLocationData , work_number : int) -> int:
        
        for _ in range(work_number):
            self.exp_gained += location.work_one_job()
            self.energy -= 1
    
            
        

class SimulatorWorkCycle():
    
    def __init__(self,
                 player_data : Player_data ,
                 time_limit : int ,
                 work_duration : int = 15 ,
                 energy_usable : SimulUsableItem | None = None ,
                 motivation_usable : SimulUsableItem | None = None ,
    ):
        self.player_data = player_data
        self.time_limit = time_limit
        self.energy_max = self.player_data.energy_max
        self.work_duration = work_duration
        self.energy_usable = energy_usable
        self.motivation_usable = motivation_usable

    def _calculate_actions(self , simulation : WorkCycleSimulation) -> list[tuple[int,SimulationLocationData]]:
        
        actions = []
        actions_possible = simulation.energy
        
        for job in simulation.simul_location_data:

            
            work_action = min(job.motivation - 75 , actions_possible)
            
            if work_action != 0:
                actions.append((work_action,job))
                
                actions_possible -= work_action
            
            if actions_possible == 0:
                return actions
        
        return actions
    
    def _work_actions(self,
              simulation : WorkCycleSimulation,
              event_list: list[tuple[int,SimulationLocationData]]) -> bool:
        
        for num_work,job_data in event_list:
            
            simulation.go_to_location(location = job_data)
            simulation.work(location = job_data , work_number = num_work)
            
            if simulation.elapsed_time > self.time_limit:
                return False
            
        return True
    
    def _work_cycle(self,
                    simulation : WorkCycleSimulation
                    ):
        
        actions = self._calculate_actions(simulation= simulation)
        
        if len(actions) == 0:
            
            return True
        
        result = self._work_actions(simulation = simulation ,
                           event_list= actions
                           )
        
        return result
        
            
    
    def simulate(self , work_cycle_simul : WorkCycleSimul) -> WorkCycleSimulation:
        
        simulation = WorkCycleSimulation(
            player_data= self.player_data,
            energy= self.energy_max,
            work_time= self.work_duration,
            work_cycle_simul = work_cycle_simul,
            energy_usable= self.energy_usable,
            motivation_usable = self.motivation_usable
        )
        
        while simulation.elapsed_time < self.time_limit:
            
            if simulation.energy == 0 :
                
                used = simulation.use_energy_consumable()
                if not used:
                    break
            
            result = self._work_cycle(simulation=simulation)
            
            if not result:
                return simulation
            
            if simulation.elapsed_time > self.time_limit:
                return simulation

            if simulation.energy > 0 and not simulation.can_afford_motivation_wise():
                
                used = simulation.use_motivation_consumable()
                if not used:
                    break
        
        return simulation