
import time
import typing
from the_west_inner.bag import Bag
from the_west_inner.currency import Currency
from the_west_inner.traveling_merchant import Travelling_merchant_manager
from the_west_inner.items import Items


class SellOrder:
    
    def __init__(self , item_id : int , item_price : int, item_number : int = 1 ):
        self.item_id = item_id
        self.item_number = item_number
        self.item_price = item_price
    

class SellDecisionManager:
    
    def __init__(self , bag : Bag , items : Items,item_exception_list : list[int] | None = None):
        
        self.bag = bag
        self.items = items
        self.item_exception_list = [] if item_exception_list is None else item_exception_list
    
    def decide_sell(self ) -> typing.Generator[SellOrder , None , None]:
        
        bad_item_type = ['yield' , 'recipe']
        
        sell_dict = {x : y for x,y in  self.items.items.items() 
                        if y.get('dropable') == True 
                        if y.get('type') not in bad_item_type 
                        if x not in self.item_exception_list
                        }
        
        for item_id , item_dict in sell_dict.items():
            
            number = self.bag[int(item_id)]
            
            if number > 0:
                
                yield SellOrder(
                    item_id = int(item_id),
                    item_price= item_dict.get('sell_price'),
                    item_number= number
                )
    def decide_sell_list(self , list_items : list[int]) -> typing.Generator[SellOrder, None , None]:
        
        bad_item_type = ['yield' , 'recipe']
        
        sell_dict = {x : y for x,y in  self.items.items.items() 
                        if y.get('dropable') == True 
                        if y.get('type') not in bad_item_type 
                        if x not in self.item_exception_list
                        if x in list_items
                        }
        for item_id , item_dict in sell_dict.items():
            
            number = self.bag[int(item_id)]
            
            if number > 0:
                
                yield SellOrder(
                    item_id = int(item_id),
                    item_price= item_dict.get('sell_price'),
                    item_number= number
                )

class SellManager:
    
    def __init__(self,travelling_merchant_manager :Travelling_merchant_manager ,
                 currency : Currency,
                 items : Items
                 ):
        self.travelling_merchant_manager = travelling_merchant_manager
        self.currency = currency
        self.items = items
    
    def _sell(self , sell_order : SellOrder) -> int:
        initial_money = self.currency.total_money
        self.travelling_merchant_manager.sell_item(
                item_id = sell_order.item_id,
                amount= sell_order.item_number
            )
        if self.currency.total_money - initial_money != sell_order.item_price * sell_order.item_number:
            
            raise ValueError(f'You sold and got {self.currency.total_money - initial_money } instead of expected {sell_order.item_price * sell_order.item_number}')
        
        return self.currency.total_money - initial_money
    def sell(self , sell_order_generator : typing.Generator[SellOrder , None , None] , pause : int | None = None) -> int:
        ammount = 0
        total_number = 0
        for sell_order in sell_order_generator:
            item_name = self.items.find_item(item_id = sell_order.item_id).get('name')
            print(f"Selling {item_name} : {sell_order.item_number}")
            if pause is not None:
                time.sleep(pause)
            result = self._sell(sell_order = sell_order)
            print(f'Sold for {result}')
            
            ammount += result
            total_number += sell_order.item_number
        
        print('-' * 30)
        print(f'Sold {total_number} items for {ammount} $')
        
        return ammount