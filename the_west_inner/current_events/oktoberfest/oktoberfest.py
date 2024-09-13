from datetime import datetime
import typing
from pydantic import BaseModel

from the_west_inner.currency import Currency
from the_west_inner.current_events.current_event_data import CurrencyData, CurrentEventData, EventCurrencyEnum, EventStageData
from the_west_inner.current_events.current_event_handler import EventHandler
from the_west_inner.current_events.current_events import CurrentEvent
from the_west_inner.misc_scripts import turn_game_time_to_datetime


class OktoberfestBuildingData(BaseModel):
    construction_id : typing.Literal[0,25,150,800]
    being_built : bool = False
    collected : bool = False
    finish_date : datetime | None = None
    stage : int = 0
    @staticmethod
    def build_from_dict(dict_data : dict[str , str]) -> typing.Self:
        return OktoberfestBuildingData(
            construction_id = dict_data.get('construction_id'),
            being_built = dict_data.get('being_built'),
            collected = dict_data.get('collected'),
            finish_date = turn_game_time_to_datetime(
                        dict_data.get('finish_date')
                        ) if dict_data.get('finish_date') else None,
            stage = dict_data.get('stage')
            
        )
    
    def get_build_cost(self, event_currency: EventCurrencyEnum , stage_data : EventStageData) -> int:
        return stage_data.get_bet_cost_by_stage(stage = self.construction_id,
                                                event_currency = event_currency
                                                )
    
    def can_afford_build(self,
                  currency_type : EventCurrencyEnum ,
                  global_currency : Currency ,
                  event_currency_ammount : int,
                  stage_data : EventStageData,
                  currency_data : CurrencyData
                  ) -> bool:
        cost = self.get_build_cost(event_currency =currency_type,
                                   stage_data = stage_data
                                   )
        
        bribe_cost = currency_data.get_bribe_cost(currency= currency_type)
        
        if currency_type.value == 2 :
            return global_currency.nuggets >= cost + bribe_cost
        
        return event_currency_ammount >= cost + bribe_cost
    
    def can_build(self,
                  currency_type : EventCurrencyEnum ,
                  global_currency : Currency ,
                  event_currency_ammount : int,
                  stage_data : EventStageData,
                  currency_data : CurrencyData
                  ) -> bool:
        return not self.being_built and self.can_afford_build(
            currency_type=currency_type,
            global_currency=global_currency,
            event_currency_ammount=event_currency_ammount,
            stage_data=stage_data,
            currency_data= currency_data
        )

class OktoberfestEventData:
    def __init__(self , buildings : list[OktoberfestBuildingData]):
        self.buildings = buildings
        self._complete_buildings()
    
    def _complete_buildings(self) :
        
        new_buildings = []
        
        buildings_dict = {x.construction_id : x for x in self.buildings}
        
        for building_slot in [0,25,150,800]:
            
            building = buildings_dict.get(building_slot , OktoberfestBuildingData(construction_id = building_slot))
            new_buildings.append(building)
        
        self.buildings = new_buildings
            
    def _create_update_building(self , update_dict : dict) -> OktoberfestBuildingData:
        
        finish_time = turn_game_time_to_datetime(game_time = update_dict.get('finish_date'))
        
        return OktoberfestBuildingData(
            construction_id = update_dict.get('construction_id'),
            being_built = True,
            collected = True ,
            finish_date = finish_time,
            stage= update_dict.get('building_stage')
        )
        
        
    def update_buildings(self, updated_data : typing.Iterable[dict]) -> None:
        
        updated_building = self._create_update_building(update_dict = updated_data)
        def replace(x : OktoberfestBuildingData) -> OktoberfestBuildingData:
            if x.construction_id == updated_building.construction_id :
                return updated_building
            return x
        
        self.buildings = list(map(replace , self.buildings))
        
        
    def return_collectable(self,
                           currency_type : EventCurrencyEnum ,
                           global_currency : Currency ,
                           event_currency_ammount : int,
                           stage_data : EventStageData,
                           currency_data : CurrencyData
                  ) -> list[OktoberfestBuildingData]:
        
        return [ x for x in self.buildings if x.can_build(currency_type=currency_type,
                                                          global_currency= global_currency,
                                                          event_currency_ammount= event_currency_ammount,
                                                          stage_data= stage_data,
                                                          currency_data= currency_data
                                                          )
                ]
    
    def return_by_offset(self, offset : typing.Literal[0,1,2,3]) -> OktoberfestBuildingData:
        return self.buildings[offset]
    
    def return_by_id(self, building_id : typing.Literal[0,25,150,800]) -> OktoberfestBuildingData:
        for building in self.buildings:
            if building.construction_id == building_id:
                return building
        raise Exception(f'You should have gotten a building but you did not . You used {building_id} id')


OffsetType : typing.TypeAlias = typing.Literal[0,1,2,3]


class OktoberfestEvent(CurrentEvent):
    
    def __init__(self ,
                 currency : Currency ,
                 event_handler : EventHandler , 
                 current_event_data : CurrentEventData,
                 oktoberfest_event_data : OktoberfestEventData
                 ):
        self.global_currency = currency
        self.event_handler = event_handler
        self.current_event_data = current_event_data
        self.oktoberfest_event_data = oktoberfest_event_data
    
    def get_building_id(self , oktoberfest_event_building : OktoberfestBuildingData|OffsetType) -> int:
        
        if isinstance(oktoberfest_event_building , OktoberfestBuildingData):
            
            return oktoberfest_event_building.construction_id
        
        return self.current_event_data.event_stage_data.gamble_stages[oktoberfest_event_building]
    def _update_buildings(self,response_dict : dict[str,str|dict]):
        self.oktoberfest_event_data.update_buildings(updated_data=response_dict)
    def _handle_succesful_construction(self , cost : int , currency_type : EventCurrencyEnum , response : dict[str:dict|str]):
        
        if currency_type.value == 2:
            new_nuggets = self.global_currency.nuggets - cost
            self.global_currency.set_nuggets(new_nuggets =  new_nuggets)
        else :
            self.current_event_data.event_currency_ammount.add_currency(value= -cost)
        
        self._update_buildings(response_dict=response)
        
    def bid_by_offset(self, offset : typing.Literal[0,1,2,3] , currency_type : EventCurrencyEnum):
        
        building = self.oktoberfest_event_data.return_by_offset(offset=offset)
        
        if building.being_built :
            raise Exception('Tried to build a building that already in construction !')
        
        if not building.can_build(
            currency_type = currency_type,
            global_currency=self.global_currency,
            event_currency_ammount = self.current_event_data.currency_ammount,
            stage_data = self.current_event_data.event_stage_data,
            currency_data = self.current_event_data.currency_data
        ):
            raise Exception('You tried to build something that cannot be built because you cannot afford it')
        
        cost = building.get_build_cost(
            event_currency = currency_type,
            stage_data = self.current_event_data.event_stage_data
        )
        
        bribe_cost = self.current_event_data.currency_data.get_bribe_cost(currency= currency_type)
        
        
        result = self.event_handler.gamble(
            pay_id = currency_type.value,
            gamble_level = building.construction_id ,
            wof_id = self.current_event_data.event_wof
        )
        
        if result.get('failed') :
            print('bribing ')
            bribe_result = self.event_handler.bribe(pay_id = currency_type.value,
                                     wof_id= self.current_event_data.event_wof
                                     )
            cost += bribe_cost
            print(bribe_result)
        
        self._handle_succesful_construction(
            cost = cost,
            currency_type =currency_type ,
            response = result
        )
    
    @property
    def currency(self)->int:
        return self.current_event_data.currency_ammount
    
    def can_build_by_offset(self , offset : typing.Literal[0,1,2,3] , currency_type : EventCurrencyEnum) -> bool:
        
        event_building = self.oktoberfest_event_data.return_by_offset(offset=offset)
        
        return event_building.can_build(
            currency_type = currency_type,
            global_currency = self.global_currency,
            event_currency_ammount = self.currency,
            stage_data = self.current_event_data.event_stage_data,
            currency_data = self.current_event_data.currency_data
        )