import typing
from datetime import datetime
from pydantic import BaseModel

from the_west_inner.misc_scripts import turn_game_time_to_datetime
from the_west_inner.currency import Currency

from the_west_inner.current_events.current_event_data import CurrentEventData,EventCurrencyEnum,EventStageData
from the_west_inner.current_events.current_event_handler import EventHandler

class IndependenceBuildingData(BaseModel):
    construction_id : typing.Literal[0,25,150,800]
    being_built : bool
    built_points : int
    collected : bool
    finish_date : datetime | None
    next_build_time : int
    stage : int
    
    def build_from_dict(self, dict_data : dict[str , str]) -> typing.Self:
        
        return IndependenceBuildingData(
            construction_id = dict_data.get('construction_id'),
            being_built = dict_data.get('construction_id'),
            built_points = dict_data.get('build_points'),
            collected = dict_data.get('collected'),
            finish_date = turn_game_time_to_datetime(
                        dict_data.get('finish_date')
                        ) if dict_data.get('finish_date') else None,
            next_build_time = dict_data.get('next_build_time'),
            stage = dict_data.get('stage')
            
        )
    def check_if_collectable(self) -> bool:
        
        return not self.being_built and not self.collected
    
    def get_build_cost(self, event_currency: EventCurrencyEnum , stage_data : EventStageData) -> int:
        return stage_data.get_bet_cost_by_stage(stage = self.construction_id,
                                                event_currency = event_currency
                                                )
    
    def can_afford_build(self,
                  currency_type : EventCurrencyEnum ,
                  global_currency : Currency ,
                  event_currency_ammount : int,
                  stage_data : EventStageData
                  ) -> bool:
        cost = self.get_build_cost(event_currency =currency_type,
                                   stage_data = stage_data
                                   )
        if currency_type.value == 2 :
            return global_currency.nuggets >= cost
        
        return event_currency_ammount >= cost
    
    def can_build(self,
                  currency_type : EventCurrencyEnum ,
                  global_currency : Currency ,
                  event_currency_ammount : int,
                  stage_data : EventStageData
                  ) -> bool:
        return not self.being_built and self.can_afford_build(
            currency_type=currency_type,
            global_currency=global_currency,
            event_currency_ammount=event_currency_ammount,
            stage_data=stage_data
        )

class IndependenceEventData:
    def __init__(self , buildings : list[IndependenceBuildingData]):
        self.buildings = buildings
    
    
    def return_collectable(self) -> list[IndependenceBuildingData]:
        
        return [ x for x in self.buildings if not x.check_if_collectable()]
    
    def return_by_offset(self, offset : typing.Literal[0,1,2,3]) -> IndependenceBuildingData:
        return self.buildings[offset]
    
    def return_by_id(self, building_id : typing.Literal[0,25,150,800]) -> IndependenceBuildingData:
        for building in self.buildings:
            if building.construction_id == building_id:
                return building
        raise Exception(f'You should have gotten a building but you did not . You used {building_id} id')

OffsetType : typing.TypeAlias = typing.Literal[0,1,2,3]

class IndependenceEvent:
    
    def __init__(self ,
                 currency : Currency ,
                 event_handler : EventHandler , 
                 current_event_data : CurrentEventData,
                 independence_event_data : IndependenceEventData
                 ):
        self.global_currency = currency
        self.event_handler = event_handler
        self.current_event_data = current_event_data
        self.independence_event_data = independence_event_data
    
    def get_building_id(self , independence_event_building : IndependenceBuildingData|OffsetType) -> int:
        
        if isinstance(independence_event_building , IndependenceBuildingData):
            
            return independence_event_building.construction_id
        
        return self.current_event_data.event_stage_data.gamble_stages[independence_event_building]
    
    def collect_building(self,independence_event_building : IndependenceBuildingData|OffsetType):
        
        building_id = self.get_building_id(independence_event_building = independence_event_building)
        
        self.event_handler.collect(
            gamble_level = building_id ,
            wof_id = self.current_event_data.event_wof
        )
    
    def build_by_offset(self, offset : typing.Literal[0,1,2,3] , currency_type : EventCurrencyEnum):
        
        building = self.independence_event_data.return_by_offset(offset=offset)
        
        if building.being_built :
            raise Exception('Tried to build a building that already in construction !')
        
        if not building.can_afford_build(
            currency_type = currency_type,
            global_currency=self.global_currency,
            event_currency_ammount = self.current_event_data.currency_ammount,
            stage_data = self.current_event_data.event_stage_data
        ):
            raise Exception('You tried to build something that cannot be built because you cannot afford it')
        
        result = self.event_handler.gamble(
            pay_id = currency_type.value,
            gamble_level = building.construction_id ,
            wof_id = self.current_event_data.event_wof
        )
        
        if currency_type.value == 2:
            new_nugget = self.global_currency
            self.global_currency.set_nuggets(new_nuggets = 
                                            )