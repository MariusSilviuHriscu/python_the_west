from dataclasses import dataclass

from the_west_inner.requests_handler import requests_handler
from the_west_inner.towns import Town_list,TownSortKey
from the_west_inner.player_data import Player_data

@dataclass
class Currency:
    
    cash : int
    deposit : int
    oup : int
    nuggets : int
    veteran_points : int
    max_oup : int = 3000
    @property
    def total_money(self) -> int :
        return self.cash + self.deposit

    def add_cash(self , ammount : int) :
        self.cash  += ammount
    
    def consume_money(self, ammount : int) :
        if ammount > self.total_money :
            raise ValueError(f"Can't spend {ammount} when you only have {self.total_money} ! ")
        if ammount > self.cash :
            self.deposit = self.deposit - ammount + self.cash
            self.cash = 0
        else:
            self.cash = self.cash - ammount 
    def modify_cash(self,new_cash:int):
        self.cash = new_cash
    def modify_money(self , new_cash : int, new_deposit : int):
        self.cash = new_cash
        self.deposit = new_deposit
    
    def modify_oup(self, oup_delta : int) :
        
        if self.oup + oup_delta < 0 :
            raise ValueError('Tried subtracting more oup than possible !')
        if self.oup + oup_delta > self.max_oup:
            raise ValueError('Tried to add too many oup')
        
        self.oup = self.oup + oup_delta
    def set_oup(self,new_oup:int):
        self.oup = new_oup
    def set_veteran_points(self,new_veteran_points:int):
        self.veteran_points = new_veteran_points
    def set_nuggets(self,new_nuggets:int):
        self.nuggets = new_nuggets
    def _update_raw(self , handler : requests_handler , town_id : int):
        
        response = handler.post(window='building_bank',
                                action = 'get_data',
                                action_name= 'mode',
                                payload = {'town_id': f'{town_id}'}
                                )
        
        if 'error' in response and response.get('error') :
            raise Exception(f'Could not properly request bank data town id :{town_id}')
        
        return response
        
    def update_raw(self , town_list : Town_list, requests_handler : requests_handler , player_data : Player_data):
        
        sort_key = TownSortKey(handler=requests_handler)
        
        town = town_list.get_closest_town(player_data = player_data , key = sort_key.bank_available_sorting_key)
        
        response = self._update_raw(handler = requests_handler , town_id= town.town_id)
        
        self.modify_money(new_cash = response.get('own_money') ,
                          new_deposit = response.get('deposit')
                          )
    def _update_raw_oup(self, handler : requests_handler):
        
        response = handler.post(
            window='daily',
            action='log',
            action_name='mode'
        )
        print(response)
        if response.get('error', False):
            
            raise Exception(f'Could not raw update oup ! ')
        
        data = response.get('msg')
        received_oup_data = data.get('log')
        
        return received_oup_data
    
    def update_raw_oup(self , handler : requests_handler):
        
        oup_data = self._update_raw_oup(
            handler=handler
        )
        if len(oup_data) == 0 :
            return
        
        
        last_oup_data = oup_data[0]
        new_oup = last_oup_data.get('coupon_carrying')
        
        self.set_oup(new_oup= new_oup)
        
        
        

def build_currency(input_dict:dict) -> Currency:
    return Currency(cash = input_dict['cash'],
                    deposit = input_dict['deposit'],
                    oup = input_dict['upb'],
                    nuggets = input_dict['nuggets'],
                    veteran_points = input_dict['veteranPoints'],
                    max_oup = 3000
                    )
