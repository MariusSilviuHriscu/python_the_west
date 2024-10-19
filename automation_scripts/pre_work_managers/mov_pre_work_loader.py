from the_west_inner.equipment import Equipment
from the_west_inner.game_classes import Game_classes
from the_west_inner.player_data import Player_data
from the_west_inner.work import Work
from the_west_inner.work_job_data import WorkDataLoader, WorkJobDataManager
from the_west_inner.map import MapLoader

from automation_scripts.pre_work_managers.mov_pre_work_managers import PreWorkMovementManager,WorkMovementTableType
from the_west_inner.work_list import Work_list

class PreWorkMovDecisionMaker:
    
    def __init__(self , 
                 work_list  : Work_list,
                 player_data : Player_data
                 ):
        self.work_list = work_list
        self.player_data = player_data
        
    def get_jobs(self , work_id : int) -> list[int]:
        
        group_id = self.work_list.get_group_id(work_id = work_id)
        return self.work_list.get_jobs_by_group_id(group_id = group_id)
    
    def has_enough_levels(self , work_id : int) -> bool:
        
        return self.player_data.level >= self.work_list.get_work_level(work_id = work_id)
        
    def _decide(self , job_data_manager : WorkJobDataManager , work_id : int) -> bool:
        
        work_job_data = job_data_manager.get_by_id(work_id = work_id)
        
        return work_job_data.work_points > 0 or self.has_enough_levels(work_id = work_id)
    
    def decide(self, job_data_manager : WorkJobDataManager , work : Work) -> Work:
        
        jobs = self.get_jobs(work_id = work.job_id )
        
        for job_id in jobs :
            
            if self._decide(job_data_manager = job_data_manager,
                            work_id = job_id
                            ):
                return Work(
                    job_id= job_id,
                    x = work.x,
                    y = work.y,
                    duration = 15
                )
        raise ValueError('Could not find a good enough route !')
        
        

class PreWorkMovManagerBuilder:
    def __init__(self,
                game_classes : Game_classes
                ):
        
        self.game_classes = game_classes
        self.decision_maker = PreWorkMovDecisionMaker(
            work_list = self.game_classes.work_list,
            player_data = self.game_classes.player_data
        )
    
    def _build(self, 
               work_list : list[Work] ,
               job_data_manager : WorkJobDataManager ,
               movement_equipment: Equipment
               ) -> PreWorkMovementManager:
        movement_table : WorkMovementTableType = {}
        for work in work_list:
            
            
            target = self.decision_maker.decide(
                job_data_manager = job_data_manager,
                work = work
            )
            movement_table[(work.job_id ,work.x , work.y)] = target
        
        return PreWorkMovementManager(
            work_table  = movement_table,
            work_manager = self.game_classes.work_manager,
            movement_equipment=movement_equipment,
            equipment_manager=self.game_classes.equipment_manager,
            movement_manager=self.game_classes.movement_manager
        )
    
    def _make_work_manager(self) -> WorkJobDataManager:
        

        map_loader = MapLoader(
            handler= self.game_classes.handler,
            player_data= self.game_classes.player_data,
            work_list = self.game_classes.work_list
        )
        work_loader = WorkDataLoader(
            handler= self.game_classes.handler,
            player_data = self.game_classes.player_data,
            map = map_loader.build()
        )
        
        return work_loader.get_work_data_manager()
        
        
    def build(self , 
            work_list : list[Work],
            movement_equipment : Equipment) -> PreWorkMovementManager:
        
        with self.game_classes.equipment_manager.temporary_equipment(
            new_equipment = movement_equipment , 
            handler= self.game_classes.handler
            ):
            
            return self._build(
                work_list = work_list,
                job_data_manager = self._make_work_manager(),
                movement_equipment = movement_equipment
            )