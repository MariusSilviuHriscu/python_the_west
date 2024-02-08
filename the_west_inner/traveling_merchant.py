import typing
from dataclasses import dataclass
import warnings
from enum import Enum

from bidict import bidict

from currency import Currency
from bag import Bag
from requests_handler import requests_handler
from items import Items


# Dictionary to map currency type IDs to their names
TRAVELLING_MARKET_CURRENCY_DICT = bidict({
    1: 'bonds',
    2: 'nuggets',
    4: 'dollar',
    8: 'veteran',
    3: 'combination_type'
})

@dataclass
class Travelling_market_offer:
    currency_type_id: int
    item_id: int
    price_bonds: int
    price_dollars: int
    price_nuggets: int
    price_veteran: int
    tab : str

    def can_afford(self, currency: Currency, preference: int = 0, currency_type_id=None) -> bool:
        """
        Check if the player can afford the Travelling Market offer based on the provided currency.

        Args:
            currency (Currency): The player's currency.
            preference (int): The preferred currency type (for combination_type). Defaults to 0.
            currency_type_id (int): The specific currency type to check. Defaults to None.

        Returns:
            bool: True if the player can afford the offer, False otherwise.
        """

        # If currency_type_id is not provided, use the one from the offer
        if currency_type_id is None:
            currency_type_id = self.currency_type_id

        # Get the name of the currency type
        currency_type_name = TRAVELLING_MARKET_CURRENCY_DICT.get(currency_type_id, None)

        # Check affordability based on the currency type
        if currency_type_name == 'bonds':
            return self.price_bonds <= currency.oup
        elif currency_type_name == 'nuggets':
            return self.price_nuggets <= currency.nuggets
        elif currency_type_name == 'dollar':
            return self.price_dollars <= currency.total_money
        elif currency_type_name == 'veteran':
            return self.price_veteran <= currency.veteran_points
        elif currency_type_name == 'combination_type':
            # For combination_type, check affordability based on the preferred currency
            return self.can_afford(currency=currency, currency_type_id=preference)
        else:
            # Unknown currency type
            raise ValueError(f"Unknown currency type ID: {currency_type_id}")
    def _buy_offer(self,handler:requests_handler,currency_type_id:int):
        payload = {
                    'item_id': self.item_id,
                    'category' : f'{self.tab}',
                    'currency' : currency_type_id
                    }
        result = handler.post(window='shop_trader',action='buy',payload=payload,use_h=True)
        
        if result['error']:
            raise Exception(f"Something went wrong buyin the offer : {result['msg']}")
        
        return result
        
    def buy(self ,handler : requests_handler, currency : Currency , bag:Bag , prefered_currency_id:int = None):
        
        if prefered_currency_id is None:
            
            prefered_currency_id = self.currency_type_id
            
        
        if bag.requires_inventory_reload :
            bag.update_inventory(handler = handler)
        
        if not self.can_afford(currency = currency,preference = prefered_currency_id):
            
            raise ValueError('Cannot affort to buy that in your prefered currency!')
        
        response = self._buy_offer(handler=handler,currency_type_id=prefered_currency_id)
        
        bag.update_inventory(handler=handler)
        
        deposit = response.get('deposit',None)
        cash = response.get('cash',None)
        oup = response.get('bonds',None)
        nuggets = response.get('nuggets',None)
        veteran_points = response.get('veteran',None)
        
        if deposit is not None and cash is not None:
            currency.modify_money(new_cash=cash,new_deposit=deposit)
        
        if oup is not None:
            currency.set_oup(new_oup=oup)
        
        if nuggets is not None:
            currency.set_nuggets(new_nuggets=nuggets)
        
        if veteran_points is not None:
            currency.set_veteran_points(new_veteran_points=veteran_points)
        
        return True

class Travelling_merchant_type_enum(Enum):
    CHESTS = 'chests'
    TRADER = 'trader'
    USEABLES = 'useables'
    EQUIP = 'equip'

class TravellingMarketplaceOfferList:
        
    def __init__(self,
                 marketplace_offer_dict : dict[int,Travelling_market_offer]
                 ):
        self.marketplace_offer_dict = marketplace_offer_dict
    
    def __getitem__(self , n : int):
        
        return self.marketplace_offer_dict[n]
    def get_by_item_id(self,item_id:int):
        
        return self.__getitem__(item_id)
    
    def buy_by_id(self,item_id:int,handler:requests_handler,currency:Currency,bag:Bag,prefered_currency_id:int):
        
        offer = self.get_by_item_id(item_id = item_id)
        return offer.buy(
            handler = handler ,
            currency = currency ,
            bag = bag ,
            prefered_currency_id = prefered_currency_id
        )
    def __add__(self, other:typing.Self) -> typing.Self:
        return TravellingMarketplaceOfferList(
            marketplace_offer_dict = {**self.marketplace_offer_dict,**other.marketplace_offer_dict}
        )
    
    def get_by_type(self,type_str:Travelling_merchant_type_enum) -> typing.Self:
        
        return TravellingMarketplaceOfferList(
            marketplace_offer_dict = { x:y for x,y in self.marketplace_offer_dict.items() if y.tab == type_str.value}
        )
    
    def get_item_id_list(self) -> list[int]:
        
        return [x for x in self.marketplace_offer_dict.keys()]
    
    def __contains__(self,item_id:int):
        
        return item_id in self.marketplace_offer_dict
    
    def sort(self, key: typing.Optional[typing.Callable[[Travelling_market_offer],int]] = None, reverse: bool = False) -> None:
        """
        Sort the marketplace offers based on the provided key and order.

        Args:
            key (Optional[Callable]): A callable used as the sorting key.
            reverse (bool): Flag to specify whether to reverse the order.

        Returns:
            None
        """
        self.marketplace_offer_dict = dict(sorted(self.marketplace_offer_dict.items(), key=lambda x: key(x[1]), reverse=reverse))
    
    def get_first(self) -> typing.Optional[Travelling_market_offer]:
        """
        Get the first marketplace offer.
    
        Returns:
            Optional[Travelling_market_offer]: The first marketplace offer or None if the list is empty.
        """
        return next(iter(self.marketplace_offer_dict.values()), None)


class TravellingMerchantOfferSearchManager():
    def __init__(self,handler:requests_handler):
        
        self.handler = handler
    
    def _create_offer(self,offer_dict : dict) -> tuple[int,Travelling_market_offer]:
        
        return offer_dict['item_id'] , Travelling_market_offer(
            currency_type_id = offer_dict['currency'],
            item_id = offer_dict['item_id'] ,
            price_bonds = offer_dict.get('price_bonds',0) ,
            price_dollars = offer_dict.get('price_dollar',0) ,
            price_nuggets = offer_dict.get('price_nuggets',0) ,
            price_veteran= offer_dict.get('price_veteran',0),
            tab = offer_dict.get('tab')
            )
            
    
    def _request_data(self):
        
        payload = {'source':'reload'}
        response = self.handler.post(window='shop_trader',action='index',action_name='mode',payload=payload)
        return response
    
    def _load_tab_data(self,tab_data:list[dict]) -> TravellingMarketplaceOfferList:
        tab_dict = {}
        for offer in tab_data:
            item_id,travelling_market_offer = self._create_offer(offer_dict = offer)
            tab_dict[item_id] = travelling_market_offer
        
        return TravellingMarketplaceOfferList(
            marketplace_offer_dict = tab_dict
        )
    
    
    def load_data(self) ->TravellingMarketplaceOfferList:
        premium_tab_key = 'longtimer'
        
        data = self._request_data()
        trader_tab_data : dict = data['inventory']
        trader_tab_data.pop(premium_tab_key,None)
        travelling_market_offer_list = TravellingMarketplaceOfferList(marketplace_offer_dict={})
        for tab_data in trader_tab_data.values():
            
            travelling_market_offer_list = travelling_market_offer_list + self._load_tab_data(tab_data=tab_data)
        
        return travelling_market_offer_list
            

class Travelling_merchant_manager():
    def __init__(self,handler : requests_handler , bag : Bag ,items:Items, currency : Currency):
        
        self.handler = handler
        self.bag = bag
        self.currency = currency
        self.items = items
        
        self.travelling_merchant_search_manager = TravellingMerchantOfferSearchManager(handler=handler)
        self._offer_list = None
    
    def deload_list(self):
        self._offer_list = None
    def load_list(self):
        self._offer_list = self.travelling_merchant_search_manager.load_data()
    @property
    def offer_list(self) -> TravellingMarketplaceOfferList:
        if self._offer_list is None:
            self.load_list()
        
        return self._offer_list
        
    def _sell(self , inv_id : int, count: int,last_inv_id : int) -> dict:
        
        payload = {
            'inv_id': inv_id,
            'count' : count,
            'last_inv_id' :last_inv_id
        }
        response = self.handler.post(window='shop_trader',action='sell',payload = payload,use_h=True) 
        
        if response['error']:
            raise Exception('Could not sell item !')
        
        return response
        
    def sell_item(self , item_id : int , ammount : int = 1):
        
        
        if self.bag.requires_inventory_reload :
            self.bag.update_inventory(handler = self.handler)

        if self.bag[item_id] < ammount:
            raise ValueError('You want to sell more items than available in the inventory !!')
        
        item_type = self.items.find_item(item_id = item_id)['type']
        if item_type =='yield' :
            warnings.warn(message='You are trying to sell yield items.')
        
        item_inv_id = self.bag.get_inv_id(item_id=item_id)
        
        response = self._sell(inv_id = item_inv_id,count=ammount,last_inv_id=self.bag.last_inv_id)
        
        new_cash = response.get('money',None)
        
        if new_cash is not None:
            self.currency.modify_cash(new_cash=new_cash)
        
        changes:list = response['changes']
        changes.reverse()
        
        #I am not sure if i should simply update the inventory anyway or handle the changes..
        self.bag.update_inventory(handler=self.handler)
        
        return changes
    
    def buy_cheapest_item_trader(self):
        
        offer_list = self.offer_list.get_by_type(type_str=Travelling_merchant_type_enum.TRADER)
        
        offer_list.sort(lambda x : x.price_dollars)
        
        offer = offer_list.get_first()
        
        offer.buy(
            handler=self.handler,
            currency=self.currency,
            bag = self.bag
        )
        
        self.deload_list()
        
        
        
    def item_is_available(self,item_id:int) ->bool:
        
        return item_id in self.offer_list
    
    def _buy_item(self,item_id:int,prefered_currency_id:int = None):
        
        return self.offer_list.buy_by_id(
            item_id = item_id,
            handler = self.handler,
            currency= self.currency,
            bag=self.bag,
            prefered_currency_id=prefered_currency_id
        )
    
    def buy_trader_item(self,item_id:int):
        
        if not self.item_is_available(item_id = item_id):
            raise Exception("You want to buy items that aren't available to sell in the travelling market!")
        
        self._buy_item(item_id=item_id)
        
        self.deload_list()
    
    def buy_non_trader_item(self,item_id:int):
        
        if not self.item_is_available(item_id = item_id):
            raise Exception("You want to buy items that aren't available to sell in the travelling market!")
        
        self._buy_item(item_id=item_id,
                       prefered_currency_id = TRAVELLING_MARKET_CURRENCY_DICT.inverse['bonds']
                       )
        
        