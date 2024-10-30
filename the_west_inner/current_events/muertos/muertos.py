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
    
    def set_reward(self , new_reward : int | None) :
        
        self.current_prize = new_reward
    
    



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
    
    def _extract_current_reward(self , data : dict) -> int:
        
        stage_data = data.get('stages')
        
        for stage in stage_data:
            if stage == []:
                continue
            if stage.get('id' , None) == self.muertos_game_data.stage:
                return stage.get('rewards').get('item')
    def _update_muertos_game_data(self , data : dict , default_flag : bool = True ):
        
        new_muertos_game_data = MuertosGameData.build_from_dict(dict_data = data.get('game'),
                                                                current_prize = self._extract_current_reward(data=data) if default_flag else None
                                                                )
        
        self.muertos_game_data = new_muertos_game_data
    
    def start_betting(self) -> bool:
        
        if self.can_bet :
            
            result = self.event_handler.start_gamble(wof_id = self.current_event_data.event_wof )
            
            self._update_muertos_game_data(data= result,default_flag=False)

        if self.muertos_game_data.can_choose_card():
            return True
        
        return False
    
    def bet(self , offset : typing.Literal[0,1,2]) -> bool:
        
        if not self.muertos_game_data.can_choose_card():
            
            raise Exception('You cannot bet !')
        
        result = self.event_handler.choose_card(
            wof_id = self.current_event_data.event_wof,
            card = offset
        )
        
        self._update_muertos_game_data(data= result)
        if not self.muertos_game_data.win():
            self.muertos_game_data.set_reward(new_reward= None)
        return self.muertos_game_data.win()
    def advance(self) :
        
        if not self.muertos_game_data.win():
            
            raise Exception('You cannot advance to the next stage ! ')
        
        result = self.event_handler.continue_bet(wof_id = self.current_event_data.event_wof)
        
        self._update_muertos_game_data(data = result, default_flag=False)
        
    
    def collect(self):
        
        if not self.muertos_game_data.is_lost() and not self.muertos_game_data.win():
            
            raise Exception('You cannot collect now ! ')
        
        result = self.event_handler.end_bet(wof_id = self.current_event_data.event_wof)
        
        self._update_muertos_game_data(data= result ,default_flag= False)