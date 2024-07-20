import typing


from the_west_inner.login import Game_login

from the_west_inner.bag import Bag
from the_west_inner.currency import Currency
from the_west_inner.equipment import Equipment

ItemIDType = int
ExchangeDictType = dict[ItemIDType, typing.Optional[int]]

class AccountData:
    
    def __init__(self ,
                 login : Game_login, 
                 bag : Bag | None = None,
                 currency : Currency | None = None,
                 current_equipment : Equipment | None = None,
                 
                 ):
        self.login = login
        self.bag = bag
        self.currency = currency
        self.current_equipment = current_equipment
    
    @property
    def is_loaded(self) -> bool:
        return self.bag is not None and self.currency is not None and self.current_equipment is not None
    def __getattribute__(self, name: str) -> typing.Any:
        
        if name in ['bag' , 'currency' , 'current_equipment'] and not self.is_loaded:
            self.load()
        match name:
            case 'login':
                return self.login
            case 'bag':
                return self.bag
            case 'currency':
                return self.currency
            case 'current_equipment':
                return self.current_equipment
            case _:
                raise AttributeError(f"'AccountData' object has no attribute '{name}'")
                
        
    def load(self):
        
        game_classes = self.login.login()
        
        self.bag = game_classes.bag
        self.currency = game_classes.currency
        self.current_equipment = game_classes.equipment_manager.current_equipment
    
    def get_item_number(self, item_id : int) -> int:
        return self.bag[item_id]
    def get_items_by_item_list(self, item_id_list : list[int]) -> ExchangeDictType :
        
        return {x : self.get_item_number(item_id = x) for x in item_id_list if self.get_item_number(item_id = x) != 0}
        
    def get_money(self ) -> int:
        
        return self.currency.total_money


class CompleteAccountData:
    def __init__(self , accounts : list[Game_login]):
        
        self.accounts : list[AccountData] = [AccountData(login=x) for x in accounts]
    
    def is_loaded(self) -> bool:
        
        return all([x.is_loaded for x in self.accounts])
    
    def load_all(self):
        
        for account_data in self.accounts:
            
            account_data.load()
    
    def get_money(self) -> int:
        return sum([x.get_money() for x in self.accounts])
    
    def get_number_of_items(self, item_id : int) -> int:
        
        return sum([x.get_item_number(item_id = item_id) for x in self.accounts])
    
    def __iter__(self) -> typing.Iterator[AccountData] :
        
        return iter(self.accounts)
    
    def get_by_id_list(self , id_list : list[int]) :
        pass