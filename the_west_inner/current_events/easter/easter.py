import typing
from datetime import datetime
from pydantic import BaseModel

from the_west_inner.misc_scripts import turn_game_time_to_datetime
from the_west_inner.currency import Currency

from the_west_inner.current_events.current_event_data import CurrencyData, CurrentEventData,EventCurrencyEnum,EventStageData
from the_west_inner.current_events.current_event_handler import EventHandler
from the_west_inner.current_events.current_events import CurrentEvent

EmptyListType = typing.Literal[[]]
class EasterBanditData(BaseModel):
    bandit_id : typing.Literal[0,25,150,800]
    finish_date : datetime | None
    won_last : bool

    def check_duel_cooldown(self) -> bool:
        
        result =  self.finish_date is None or self.finish_date < datetime.now()
        
        return result
    
    def duel_cost(self, event_currency: EventCurrencyEnum , stage_data : EventStageData) -> int:
        return stage_data.get_bet_cost_by_stage(stage = self.bandit_id,
                                                event_currency = event_currency
                                                )
    def check_if_can_afford(self, 
                           event_currency: EventCurrencyEnum , 
                           stage_data : EventStageData ,
                           currency_data : CurrencyData,
                           currency_ammount : int
                           ) -> bool:
        
        bribe_cost = currency_data.get_bribe_cost(currency=event_currency)
        duel_cost = self.duel_cost(event_currency = event_currency,
                                   stage_data = stage_data
                                   )
        
        
        return bribe_cost + duel_cost <= currency_ammount
    
    def check_if_can_duel(self,
                          event_currency: EventCurrencyEnum ,
                          stage_data : EventStageData ,
                        currency_data : CurrencyData,
                           currency_ammount : int) -> bool:
        
        return self.check_duel_cooldown() and self.check_if_can_afford(event_currency = event_currency,
                                                                      stage_data = stage_data,
                                                                      currency_data = currency_data,
                                                                      currency_ammount = currency_ammount
                                                                      )
    @staticmethod
    def build_from_dict(bandit_id : int, 
                        cooldown_data :  list[dict] | None ,
                        streak_data : list[dict] | None ) -> typing.Self:
        
        cooldown_data = (cooldown_data or [] ) if type(cooldown_data) == list else [x for x in cooldown_data.values()]
        streak_data = (streak_data or [] ) if type(streak_data) == list else [x for x in streak_data.values()]
        
        finish_date = None
        for cooldown in cooldown_data:
            if cooldown.get('enhance') == bandit_id:
                finish_date = turn_game_time_to_datetime(cooldown.get('cdstamp'))
                break
        
        won_last = True
        for streak in streak_data:
            if streak.get('enhance') == bandit_id:
                won_last = not streak.get('failed')
                break
        
        return EasterBanditData(
            bandit_id = bandit_id,
            finish_date = finish_date,
            won_last = won_last
        )

class EasterBanditsList:
    def __init__(self , bandits : list[EasterBanditData]):
        self.bandits = bandits
    
    @staticmethod
    def build_from_dict( data_dict : dict) -> typing.Self:
        
        mode_data = data_dict.get('mode')
        cooldown_data = mode_data.get('cooldowns')
        win_data = mode_data.get('enhanceStates')
        opponent_data = mode_data.get('opponentNames')
        
        bandit_list = [EasterBanditData.build_from_dict(bandit_id=int(x) , 
                                                           cooldown_data= cooldown_data ,
                                                           streak_data= win_data) 
                                    for x in opponent_data.keys()]
        
        return EasterBanditsList(bandits = bandit_list)
    
    def return_by_offset(self, offset : typing.Literal[0,1,2,3]) -> EasterBanditData:
        return self.bandits[offset]  
    def return_by_id(self, bandit_id : typing.Literal[0,25,150,800]) -> EasterBanditData:
        for bandit in self.bandits:
            if bandit.bandit_id == bandit_id:
                return bandit
        raise Exception(f'You should have gotten a bandit but you did not . You used {bandit_id} id')

OffsetType : typing.TypeAlias = typing.Literal[0,1,2,3]

class EasterEvent(CurrentEvent):
    
    def __init__(self ,
                 currency : Currency ,
                 event_handler : EventHandler , 
                 current_event_data : CurrentEventData,
                 easter_event_data : EasterBanditsList
                 ):
        self.global_currency = currency
        self.event_handler = event_handler
        self.current_event_data = current_event_data
        self.easter_event_data = easter_event_data
    
    def can_duel_by_offset(self , offset : typing.Literal[0,1,2,3] , currency_type : EventCurrencyEnum) -> bool:
        
        event_building = self.easter_event_data.return_by_offset(offset=offset)
        
        return event_building.check_if_can_duel(
            event_currency= currency_type,
            stage_data= self.current_event_data.event_stage_data,
            currency_data= self.current_event_data.currency_data,
            currency_ammount= self.currency
        )
    def get_bandit_id(self , easter_bandit : EasterBanditData|OffsetType) -> int:
        
        if isinstance(easter_bandit , EasterBanditData):
            
            return easter_bandit.bandit_id
        
        return self.easter_event_data.return_by_offset(offset=easter_bandit).bandit_id
    def _update_bandits(self,response_dict : dict[str,str|dict]):
        self.easter_event_data = EasterBanditsList.build_from_dict(data_dict = response_dict)
    
    def update_bandits(self):
        response = self.event_handler.init_event(wof_id = self.current_event_data.event_wof)
        self._update_bandits(response_dict = response)
    
    def _handle_bribe_bandit(self , currency_type : EventCurrencyEnum) -> int:
        
        response = self.event_handler.bribe(
            pay_id= currency_type.value,
            wof_id= self.current_event_data.event_wof
        )
        
        
        cost = self.current_event_data.currency_data.get_bribe_cost(currency=currency_type)
        if currency_type.value == 2:
            new_nuggets = self.global_currency.nuggets - cost
            self.global_currency.set_nuggets(new_nuggets =  new_nuggets)
        else :
            self.current_event_data.event_currency_ammount.add_currency(value= -cost)
        
        return response.get('outcome').get('itemId')
    
    def _handle_bandit_duel(self , response : dict[str,str|dict],currency_type : EventCurrencyEnum , bandit_id : int) -> int:
        
        
        cost = self.easter_event_data.return_by_id(bandit_id=bandit_id).duel_cost(event_currency=currency_type,
                                                                                 stage_data=self.current_event_data.event_stage_data)
        if currency_type.value == 2:
            new_nuggets = self.global_currency.nuggets - cost
            self.global_currency.set_nuggets(new_nuggets =  new_nuggets)
        else :
            self.current_event_data.event_currency_ammount.add_currency(value= -cost)
        
        
        if response.get('outcome') is not None:
            return response.get('outcome').get('itemId')
        
        return self._handle_bribe_bandit(currency_type = currency_type)
        
    
    def duel_bandit(self,bandit_data : EasterBanditData|OffsetType ,currency_type : EventCurrencyEnum) -> int:
        
        bandit_id = self.get_bandit_id(easter_bandit = bandit_data)
        
        response = self.event_handler.gamble(
            pay_id= currency_type.value,
            gamble_level= bandit_id,
            wof_id = self.current_event_data.event_wof
        )
        
        
        item_id = self._handle_bandit_duel(response = response , currency_type = currency_type , bandit_id=bandit_id)
        
        self.update_bandits()
        return item_id
        
    def duel_by_offset(self, offset : typing.Literal[0,1,2,3] , currency_type : EventCurrencyEnum):
        
        self.duel_bandit(bandit_data = offset , currency_type = currency_type)
    @property
    def currency(self)->int:
        return self.current_event_data.currency_ammount
