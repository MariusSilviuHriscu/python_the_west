from enum import Enum

import typing
class EventCurrencyEnum(Enum):
    
    NUGGETS = 2
    FIREWORK = 16

StageType : typing.TypeAlias = int
RewardID : typing.TypeAlias = int


UNIVERSAL_EVENT_MULTIPLIER_DICT = {2: 1 , 16 : 60}

class EventCurrency:
    
    def __init__(self , currency_key : str , currency_value : int = 0):
        self.currency_key = currency_key
        self._currency_value = currency_value
    
    @property
    def currency_value(self) -> int:
        return self._currency_value
    
    def add_currency(self , value : int ) -> None:
        
        if value + self._currency_value < 0:
            raise ValueError('Could not substract from value ')
        
        self._currency_value += value
    
    def set_value(self, value : int ) -> None:
        
        if value < 0:
            raise ValueError(f'Cannot have less than 0 {self.currency_key}')

class CostData:
    def __init__(self , bribe_cost : int , main_cost : int , reset_cost : int):
        self.bribe_cost = bribe_cost
        self.main_cost = main_cost
        self.reset_cost = reset_cost
    
    def get_cost(self, action_name : str , event_currency : EventCurrencyEnum) -> int:
        
        if action_name not in self.__dict__:
            raise ValueError(f'Incorrect action name : {action_name}')
        
        return getattr('action_name' , self) * UNIVERSAL_EVENT_MULTIPLIER_DICT.get(event_currency.value)

class CurrencyData:
    def __init__(self ,
                 cost_data : CostData,
                 bribe_dict : list[int],
                 reset_dict : list[int]
                 ):
        self.cost_data = cost_data
        self.bribe_dict = bribe_dict
        self.reset_dict = reset_dict
    
    def get_reset_cost(self, currency : EventCurrencyEnum) -> int :
        
        return self.cost_data.get_cost(action_name = 'reset_cost' ,
                                       event_currency = currency
                                       )
    
    def get_bribe_cost(self, currency : EventCurrencyEnum) -> int :
        
        return self.cost_data.get_cost(action_name = 'bribe_cost' ,
                                event_currency = currency
                                )

    
    

class DefaultRewardsData():
    def __init__(self , summary_rewards : dict[StageType , RewardID] , current_stage : StageType):
        self.summary_rewards = summary_rewards
        self.current_stage = current_stage
class EventStageData():
    
    def __init__(self , gamble_prizes : dict[StageType , list[RewardID]]):
        self.gamble_prizes = dict ( sorted ( gamble_prizes.items() ) ) # This turns the dict into a iterable of tuples , sorts that and back to dict
        self.gamble_stages = {index : stage for index , stage in enumerate(self.gamble_prizes.keys())}
    def get_bet_cost_by_offset(self, position : typing.Literal[0,1,2,3] , event_currency : EventCurrencyEnum ) -> int:
        if position not in [0,1,2,3]:
            raise ValueError(f'The position {position} is not available !')
        return self.gamble_stages.get(position ) * UNIVERSAL_EVENT_MULTIPLIER_DICT.get(event_currency.value)
    def get_bet_cost_by_stage(self, stage: typing.Literal[0,25,150,800] , event_currency : EventCurrencyEnum) -> int:
        if stage not in [0,1,2,3]:
            raise ValueError(f'The stage {stage} is not available !')
        return stage* UNIVERSAL_EVENT_MULTIPLIER_DICT.get(event_currency.value)

        
        
class CurrentEventData():
    
    
    def __init__(self , 
                 event_name : str ,
                 event_currency_ammount : EventCurrency,
                 event_wof : int,
                 enhancements : list[int],
                 can_halve_time : bool,
                 currency_data : CurrencyData,
                 event_stage_data : EventStageData
    ):
        self.event_name = event_name
        self.event_currency_ammount = event_currency_ammount
        self.event_wof = event_wof
        self.event_stages
        self.enhancements = enhancements
        self.can_halve_time = can_halve_time
        self.currency_data = currency_data
        self.event_stage_data = event_stage_data
    
    @property
    def currency_ammount(self) -> int :
        
        return self.event_currency_ammount.currency_value