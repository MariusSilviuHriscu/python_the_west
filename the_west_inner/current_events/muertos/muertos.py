from datetime import datetime
import typing
from pydantic import BaseModel

from the_west_inner.currency import Currency
from the_west_inner.current_events.current_event_data import CurrencyData, CurrentEventData, EventCurrencyEnum, EventStageData
from the_west_inner.current_events.current_event_handler import EventHandler
from the_west_inner.current_events.current_events import CurrentEvent
from the_west_inner.misc_scripts import turn_game_time_to_datetime




class MuertosGameData(BaseModel):
    free_games : int = 0
    status : str = ''
    stage : int = 0
    current_prize : int | None = None
    @staticmethod
    def build_from_dict(dict_data : dict[str , str] , current_prize : int | None) -> typing.Self:
        return MuertosGameData(
            free_games = dict_data.get('free_games'),
            status = dict_data.get('status'),
            stage = dict_data.get('current').get('stage'),
            current_prize = current_prize
        )
    
    def has_free_tries(self) -> bool:
        
        return self.free_games > 0
    def can_choose_card(self) -> bool:
        
        return self.status == 'running'
    
    def is_closed(self) -> bool:
        
        return self.status == 'closed'
    
    def is_lost(self) -> bool:
        return self.status == 'lost'
    
    def win(self) -> bool:
        
        return self.status == 'won'
    
    



OffsetType : typing.TypeAlias = typing.Literal[0,1,2,3]


class MuertosEvent(CurrentEvent):
    
    def __init__(self ,
                 currency : Currency ,
                 event_handler : EventHandler , 
                 current_event_data : CurrentEventData,
                 muertos_game_data : MuertosGameData
                 ):
        self.global_currency = currency
        self.event_handler = event_handler
        self.current_event_data = current_event_data
        self.muertos_game_data = muertos_game_data
    
    @property
    def can_bet(self) -> int:
        
        return self.muertos_game_data.has_free_tries() and self.muertos_game_data.is_closed()
    
    def bet(self) -> None:
        pass
    
    