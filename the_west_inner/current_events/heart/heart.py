from pydantic import BaseModel

from the_west_inner.currency import Currency
from the_west_inner.current_events.current_event_data import CurrentEventData , EventCurrencyEnum
from the_west_inner.current_events.current_event_handler import EventHandler
from the_west_inner.current_events.current_events import CurrentEvent
from the_west_inner.current_events.load_event_data import build_current_event_data



class CostsHeartType(BaseModel):
    oup_bet_cost : int
    nugget_bet_cost : int

HEART_COSTS = CostsHeartType(
    oup_bet_cost = 40,
    nugget_bet_cost = 8
)

class HeartEvent(CurrentEvent):
    
    def __init__(self ,
                 free_trials : int,
                 currency : Currency ,
                 event_handler : EventHandler , 
                 current_event_data : CurrentEventData,
                 
                 ):
        self.free_trials = free_trials
        self.global_currency = currency
        self.event_handler = event_handler
        self.current_event_data = current_event_data
    
    
    
    def _update_data(self, response :dict[str,str | dict]):
        
        self.current_event_data = build_current_event_data(
            response = response,
            event_currency_ammount= self.current_event_data.currency_data,
            wof_id= self.current_event_data.event_wof
        )
    
    @property
    def reward_list(self) -> list[int]:
        
        return self.current_event_data.event_stage_data.gamble_prizes.get(0)
    
    def _handle_play_currency(self , currency_type : EventCurrencyEnum) -> None:
        
        if self.free_trials > 0 :
            
            self.free_trials -= 1
            return
        if currency_type == EventCurrencyEnum.OUP :
            self.global_currency.modify_oup(oup_delta = - HEART_COSTS.oup_bet_cost )
            return
        new_nuggets = self.global_currency.nuggets - HEART_COSTS.nugget_bet_cost
        self.global_currency.set_nuggets(new_nuggets = new_nuggets)
        return
    
    def _play(self , currency_type : EventCurrencyEnum) -> dict:
        
        return self.event_handler.gamble(
            pay_id = currency_type.value ,
            wof_id = self.current_event_data.event_wof
        )
    
    def check_currency_ammounts(self , currency_type : EventCurrencyEnum) -> bool:
        
        if self.free_trials > 0:
            return True
        
        if (currency_type == EventCurrencyEnum.NUGGETS and
            self.global_currency.nuggets < HEART_COSTS.nugget_bet_cost):
            
            raise ValueError(f'Not enough nuggets : You have {self.global_currency.nuggets} but need {HEART_COSTS.nugget_bet_cost} ')
        if (currency_type == EventCurrencyEnum.OUP and
            self.global_currency.oup < HEART_COSTS.oup_bet_cost):
            
            raise ValueError(f'Not enough nuggets : You have {self.global_currency.oup} but need {HEART_COSTS.oup_bet_cost} ')
    
    def _extract_result_item(self , result : dict) -> int:
        
        return result.get('prize').get('itemId')
    
    def get_bet_cost(self,currency_type : EventCurrencyEnum) -> int :
        
        if currency_type == EventCurrencyEnum.FIREWORK:
            
            raise ValueError('Firework currency invalid!')
        
        if currency_type == EventCurrencyEnum.OUP:
            return HEART_COSTS.oup_bet_cost
        
        if currency_type == EventCurrencyEnum.NUGGETS:
            return HEART_COSTS.nugget_bet_cost

        raise ValueError('Invalid type of currency !')
        
    def get_play_times(self, currency_type : EventCurrencyEnum , limit : int = 0) -> int:
        
        if currency_type == EventCurrencyEnum.FIREWORK:
            
            raise ValueError('Firework currency invalid!')
        
        if currency_type == EventCurrencyEnum.OUP:
            return (self.global_currency.oup - limit )// self.get_bet_cost(currency_type= currency_type) + self.free_trials
        
        if currency_type == EventCurrencyEnum.NUGGETS:
            return (self.global_currency.nuggets - limit )// self.get_bet_cost(currency_type= currency_type) + self.free_trials

        raise ValueError('Invalid type of currency !')
    
    def play(self , currency_type : EventCurrencyEnum) -> int:
        
        self.check_currency_ammounts(currency_type = currency_type)
        
        result = self._play(currency_type = currency_type )
        
        self._handle_play_currency(currency_type = currency_type)
        
        return self._extract_result_item(result = result)
        
        
        
        
        
        