from dataclasses import dataclass
import datetime
import typing
from abc import ABC,abstractmethod
import dateparser

from the_west_inner.requests_handler import requests_handler
from the_west_inner.bag import Bag
from the_west_inner.player_data import Player_data
from the_west_inner.items import Items
from the_west_inner.work_manager import Work_manager


class IncorrectBuyMapPosition(Exception):
    pass


class Shop_building_interface():
    def __init__(self,shop_name:str,handler:requests_handler,bag:Bag):
        self.handler = handler
        self.shop_name = shop_name
        self.bag = bag
    def buy_item(self,item_id:int,town_id:int):
        payload = {'item_id': f'{item_id}','town_id': f'{town_id}','last_inv_id': self.bag.last_inv_id}
        response = self.handler.post(window= self.shop_name,action='buy',payload=payload,use_h= True)
        if 'error' in response:
            raise Exception("Could not buy !")
        if 'expressoffer' in response:
            raise IncorrectBuyMapPosition("You can't buy because you are not in the right position")
    def sell_item(self,item_id:int,item_number:int,town_id:int):
        payload = {'town_id': f'{town_id}','item_id': f'{item_id}','count': f'{item_number}' }
        response = self.handler.post(window= self.shop_name,action='sell',payload=payload,use_h= True)
        if 'error' in response:
            raise Exception("Could not sell!")

def load_shop_building_interface(shop_name:str,handler:requests_handler) -> Shop_building_interface:
    return Shop_building_interface(
                                shop_name = shop_name,
                                handler= handler
                                )

class ItemNotPresentInShopException(Exception):
    pass
class InvalidItemException(Exception):
    pass

@dataclass
class Building_construction_data:
    level:int
    town_id : int
    
class Shop_building():
    def __init__(self,
                shop_interface:Shop_building_interface,
                construction_data:Building_construction_data,
                available_items:list[int],
                bag:Bag,
                player_data:Player_data,
                items:Items):
        self.shop_interface = shop_interface
        self.construction_data = construction_data
        self.available_items = available_items
        self.bag = bag
        self.player_data = player_data
        self.items = items
    def _buy_item(self,item_id:int):
        if item_id not in self.items:
            raise InvalidItemException(f"The id {item_id} is not a valid item!")
        if item_id not in self.available_items:
            raise ItemNotPresentInShopException(f"Item {item_id} is not something you can buy in this shop!")
        # check for money requirement
        self.shop_interface.buy_item( item_id=item_id,town_id= self.construction_data.town_id)
    def buy_item(self,item_id:int,number :int =1):
        for _ in range(number):
            self._buy_item(item_id = item_id)
    def sell_item(self,item_id:int,number:int):
        if item_id not in self.items:
            raise InvalidItemException(f"The id {item_id} is not a valid item!")
        if self.bag[item_id] < number :
            raise ValueError("Trying to sell to many items!")
        self.shop_interface.sell_item(item_id=item_id,item_number=number,town_id= self.construction_data.town_id)

def build_shop_interface(town_id:int,
                         level : int,
                         shop_type:str,
                         available_item_list:list[int],
                         handler:requests_handler,
                         bag:Bag,
                         player_data : Player_data) -> Shop_building:
    return Shop_building(
                        shop_interface= load_shop_building_interface(shop_name=shop_type , handler= handler),
                        construction_data = Building_construction_data(level = level,town_id=town_id),
                        available_items = available_item_list,
                        bag = bag ,
                        player_data= player_data
                        )

class Building_preloader(ABC):
    pass
    @abstractmethod
    def load(self):
        pass

class Shop_building_preloader(Building_preloader):
    def __init__(self,town_id:int,shop_type : str,level:int, handler : requests_handler):
        self.town_id = town_id
        self.shop_type = shop_type
        self.level = level
        self.handler = handler
    def _get_item_list(self)  -> list[int]:
        response = self.handler.post(window = self.shop_type , action=f"{self.town_id}",action_name="town_id")
        return [x for x in response['trader_inv'].values()]
    def load(self) -> Shop_building:
        return build_shop_interface(
                                    town_id = self.town_id,
                                    level = self.level,
                                    shop_type = self.shop_type,
                                    available_item_list = self._get_item_list(),
                                    handler = self.handler,
                                    bag = self.bag,
                                    player_data = self.player_data
                                    )
class Tailor_building(Shop_building):
    pass
class Armorsmith_building(Shop_building):
    pass
class General_shop_building(Shop_building):
    pass

class Hotel_room():
    def __init__(self,
                 room_type : str,
                 price:int,
                 is_free:bool,
                 travel_distance: datetime.datetime,
                 work_manager:Work_manager,
                 target_hp:int,
                 target_energy : int,
                 is_town : bool
                 ):
        self.room_type = room_type
        self.price = price
        self.is_free = is_free
        self.travel_distance = travel_distance
        self.work_manager = work_manager
        self.target_hp = target_hp
        self.target_energy = target_energy
        self.is_town = is_town
    def sleep(self,town_id:int):
        self.work_manager.sleep_task(room_type = self.room_type,town_id = town_id)

        
class Hotel_building():
    def __init__(self,
                 construction_data:Building_construction_data,
                 chamber_list : dict[int:Hotel_room],
                 player_data : Player_data
                ):
        self.construction_data = construction_data
        self.chamber_list = chamber_list
        self.player_data = player_data
    def sleep(self,chamber_number:int) :
        if chamber_number not in self.chamber_list:
            raise ValueError(f"Chamber {chamber_number} does not exist!")
        chamber : Hotel_room = self.chamber_list[chamber_number]
        chamber.sleep(town_id=self.construction_data.town_id)

def string_to_datetime(input_str:str) -> datetime.timedelta:
    hours, minutes, seconds = map(int, input_str.split(':'))
    
    return datetime.timezonetimedelta(
                                    hours=hours,
                                    minutes=minutes,
                                    seconds=seconds)
class Hotel_building_preloader(Building_preloader):
    def __init__(self,level:int,town_id:int,handler:requests_handler,work_manager : Work_manager, player_data : Player_data) :
        self.level = level
        self.town_id = town_id
        self.handler = handler
        self.work_manager = work_manager
        self.player_data = player_data
    @staticmethod
    def _load_chamber(room_dict:dict, room_type:str, waytime:str, work_manager : Work_manager) -> Hotel_room:
        return Hotel_room(
                        room_type = room_type,
                        price = room_dict['costs'],
                        is_free = room_dict['free'],
                        travel_distance = string_to_datetime(input_str = waytime),
                        work_manager = work_manager,
                        target_hp= room_dict['health'],
                        target_energy = room_dict['energy'],
                        is_town = room_dict['type'] == 'town'
                        )

    def _get_chamber_list(self) -> list[Hotel_room]:
        
        response = self.handler.post(window='building_hotel',action='get_data',action_name='mode',payload={'town_id':f'{self.town_id}'})
        return [self._load_chamber(room_dict = room,room_type = room_type, waytime = response["waytime"],work_manager= self.work_manager) 
                        for room_type,room in response]
        
    def load(self) -> Hotel_building:
        return Hotel_building(
                            construction_data= Building_construction_data(level=self.level,town_id=self.town_id),
                            chamber_list = self._get_chamber_list(),
                            player_data = self.player_data
                            )

class Cinema_building():
    def __init__(self, construction_data: Building_construction_data,handler:requests_handler):
        self.construction_data = construction_data
        self.handler = handler
    
    def _get_video_data(self)  :
        
        response = self.handler.post(window="building_cinema",action="index",action_name="mode",payload={"town_id" : f"{self.construction_data.town_id}"})
        
        return response 

    def get_cinema_building_data(self):
        response = self._get_video_data()
        payload = {"town_id": f"{ self.construction_data.town_id }",
                    "vrid": response['video_id'],
                    "hash": response['hash'],
                    "reward": "energy"}
        
        return response['videos_left'] - 1

class Cinema_building_preloader(Building_preloader):
    def __init__(self,level :int ,town_id : int,handler:requests_handler):
        self.level = level
        self.town_id = town_id
        self.handler = handler
    def load(self) -> Cinema_building:
        return Cinema_building(
                            construction_data = Building_construction_data(level = self.level,town_id= self.town_id),
                            handler = self.handler
                            )
@dataclass
class Bank_building():
    construction_data: Building_construction_data 
    handler : requests_handler
    money:int
    deposit : int
    player_in_town : bool
    own_bank : bool
    deposit_fee : int
    can_transfer : bool
    transfer_fee : int
    def _update_money(self,ammount:int):
        self.money = ammount
    def _update_deposit(self,ammount:int):
        self.deposit = ammount 
    def deposit_money(self,ammount: int):
        if ammount > self.money:
            raise ValueError(f"You tried to deposit more money : {ammount} than you own : {self.money}")
        
        deposit_response = self.handler.post(window='building_bank',action='deposit',payload={'town_id': f'{self.construction_data.town_id}','amount': f'{ammount}'},use_h=True)
        #handle ERRORS
        if 'error' in deposit_response and deposit_response.get('error') is not False :
            raise Exception(f'Something went wrong depositing {ammount} at town : {self.construction_data.town_id}')
        self._update_money(ammount = deposit_response['own_money'])
        self._update_deposit(ammount = deposit_response['deposit'])

    def transfer_money(self,ammount : int,player_name : str,purpose:str = ""):
        if ammount > self.money:
            raise ValueError(f"You tried to transfer more money : {ammount} than you own : {self.money}")
        payload = {'town_id': f'{ammount}','player': f'{player_name}','dollar': f'{ammount}','purpose': f'{purpose}','agree': 'true'}
        transfer_response = self.handler.post(window='building_bank',action='',payload={'town_id': f'{self.construction_data.town_id}','amount': f'{ammount}'},use_h=True)
        
        if 'error' in transfer_response and transfer_response['error'] is not False:
            raise Exception(f"Something went wrong trying to transfer {ammount} $ to player {player_name} at town {self.construction_data.town_id}")

        self._update_money(ammount = transfer_response['own_money'])
        self._update_deposit(ammount = transfer_response['deposit'])
        
class Bank_building_preloader(Building_preloader):
    def __init__(self,level : int,town_id : int , handler:requests_handler) :
        self.level = level
        self.town_id = town_id
        self.handler = handler
    def _get_bank_data(self):
        bank_data_response = self.handler.post(window='bank_building',action='get_data' , payload={'town_id' : f'{self.town_id}'})
        
        if 'error' in bank_data_response and bank_data_response.get('error') is not False :
            raise Exception(f'Something went wrong getting the bank info of the city : {self.town_id}')
        
        return bank_data_response
    def load(self) -> Bank_building:
        bank_info = self._get_bank_data()
        return Bank_building(
                            construction_data = Building_construction_data(level = self.level , town_id = self.town_id),
                            handler = self.handler,
                            money = bank_info['own_money'],
                            deposit = bank_info['deposit'],
                            player_in_town = bank_info['in_town'],
                            own_bank = bank_info['own_town'],
                            deposit_fee = bank_info['deposit_fee'],
                            can_transfer = bank_info['trasfer'],
                            transfer_fee = bank_info['transfer_fee']
                            )
@dataclass
class Mortician_building:
    level:int
    duels_total: int
    duels_won: int
    duels_lost: int
    duels_diff: int
    swoon_enemies: int
    swoon_members: int
    duels_honourable: int
    duels_dishonourable: int
    duels_honour: int
    best_hit_member: int
    best_hit_member_player_id: int
    best_hit_member_name: str
    best_hit_enemy: int
    best_hit_enemy_player_id: int
    best_hit_enemy_name: str
    best_total_damage_member: int
    best_total_damage_member_player_id: int
    best_total_damage_member_name: str
    best_total_damage_enemy: int
    best_total_damage_enemy_player_id: int
    best_total_damage_enemy_name: str
class Mortician_building_preloader(Building_preloader):
    def __init__(self,level:int,handler:requests_handler,town_id:int):
        self.level = level
        self.handler = handler
        self.town_id = town_id
    def load(self):
        response = self.handler.post(window="building_mortician",action = "get_data",payload={'town_id':f'{self.town_id}'})
        
        if 'error' in response and response['error'] is not False :
            raise Exception("Could not find the mortician building!")
        
        mortician_data = response['data']
        return Mortician_building(
                                level = self.level,
                                duels_total = mortician_data["duels_total"],
                                duels_won = mortician_data["duels_won"],
                                duels_lost = mortician_data["duels_lost"],
                                duels_diff = mortician_data["duels_diff"],
                                swoon_enemies = mortician_data["swoon_enemies"],
                                swoon_members = mortician_data["swoon_members"],
                                duels_honourable = mortician_data["duels_honourable"],
                                duels_dishonourable = mortician_data["duels_dishonourable"],
                                duels_honour = mortician_data["duels_honour"],
                                best_hit_member = mortician_data["best_hit_member"],
                                best_hit_member_player_id = mortician_data["best_hit_member_player_id"],
                                best_hit_member_name = mortician_data["best_hit_member_name"],
                                best_hit_enemy = mortician_data["best_hit_enemy"],
                                best_hit_enemy_player_id = mortician_data["best_hit_enemy_player_id"],
                                best_hit_enemy_name = mortician_data["best_hit_enemy_name"],
                                best_total_damage_member = mortician_data["best_total_damage_member"],
                                best_total_damage_member_player_id = mortician_data["best_total_damage_member_player_id"],
                                best_total_damage_member_name = mortician_data["best_total_damage_member_name"],
                                best_total_damage_enemy = mortician_data["best_total_damage_enemy"],
                                best_total_damage_enemy_player_id = mortician_data["best_total_damage_enemy_player_id"],
                                best_total_damage_enemy_name = mortician_data["best_total_damage_enemy_name"]
                                )
class Church_building:
    def __init__(self,bonus:int,building_construction_data : Building_construction_data,work_manager : Work_manager):
        self.bonus = bonus
        self.building_construction_data = building_construction_data
        self.work_manager = work_manager
    def pray(self):
        self.work_manager.pray_task(town_id = self.building_construction_data.town_id)
class Church_building_preloader(Building_preloader):
    def __init__(self,level:int,handler:requests_handler,town_id:int,work_manager:Work_manager):
        self.level = level
        self.handler = handler
        self.town_id = town_id
        self.work_manager = work_manager
    def load(self) -> Church_building:
        
        response = self.handler.post(window='building_church',action='get_data',action_name='mode',payload={'town_id':f'{self.town_id}'})
        
        if 'error' in response and not response.get('error',False):
            raise Exception(f"Could not load data for the church of town: {self.town_id} !")
        
        return Church_building(
                            bonus = response.get('bonus'), 
                            building_construction_data = Building_construction_data(level = self.level , town_id = self.town_id),
                            work_manager = self.work_manager
                            )
@dataclass
class City_player_data:
    name: str
    level: int
    town_rights: int
    charclass: str
    profession_id: int
    player_id: int
    holiday: typing.Optional[str]
    title_id: int
    is_male: bool
    title: str
    status: str
    def promote(self,rank:typing.Literal[1,2,3]):
        pass
class Tenment_data():
    def __init__(self,player_list:list[City_player_data],time_limit_string: str,own_city : bool):
        self.player_list = player_list
        self.time_limit_string = time_limit_string
        self.own_city = own_city
    
    def get_time_limit(self) -> datetime.timedelta:
        return dateparser.parse(self.time_limit_string , settings={'PREFER_DATES_FROM': 'future'}) - datetime.datetime.now()

class Tenment_data_preloader(Building_preloader):
    def __init__(self,building_construction_data:Building_construction_data,handler:requests_handler):
        self.building_construction_data = building_construction_data
        self.handler = handler
    
    def load(self) ->Tenment_data:
        #TO DO
        response = self.handler.post()
        return Tenment_data(
                            player_list = [] ,
                            time_limit_string = "" ,
                            own_city= False
                            )
        

class Token_preloader(Building_preloader):
    pass
    def load(self):
        return super().load()


@dataclass
class City_hall_building_repr():
    key:str = ""
    infinite:bool = False
    max_stage:int = 0
    level : int = 0
    name:str = ""
def _load_city_hall_building(building_dict:dict):
    
    return City_hall_building_repr(
                                key = building_dict.get('key'),
                                infinite = building_dict.get('infinite'),
                                max_stage = building_dict.get('maxStage'),
                                level = building_dict.get('stage'),
                                name = building_dict.get('key') 
                                )
class City_hall_building():
    def __init__(self,building_construction_data:Building_construction_data,building_dict :dict[str,City_hall_building_repr],town_no_leave:bool):
        self.building_construction_data = building_construction_data
        self.building_dict = building_dict 
        self.town_no_leave = town_no_leave
    
    def get_building_data(self,building_key:str):
        return self.building_dict.get(building_key,City_hall_building_repr())

class City_hall_building_preloader(Building_preloader):
    def __init__(self,level:int,town_id:int,handler:requests_handler):
        self.level = level
        self.town_id = town_id
        self.handler = handler
    def load(self) -> City_hall_building:
        
        response = self.handler.post(window = 'building_cityhall',payload={'town_id':f'{self.town_id}'})
        
        building_data = response['buildings']
        
        return City_hall_building(
                                building_construction_data = Building_construction_data(level= self.level,town_id=self.town_id),
                                building_dict = {x['key'] : _load_city_hall_building(building_dict= x) for x in building_data},
                                town_no_leave = response['townNoLeave']
                                )

@dataclass
class Town_buildings:
    cityhall_loader : typing.Callable
    market_loader : typing.Callable
    tenement_loader : typing.Callable
    bank_loader : typing.Callable
    hotel_loader : typing.Callable
    gunsmith_loader : typing.Callable
    tailor_loader : typing.Callable
    general_loader : typing.Callable
    mortician_loader : typing.Callable
    church_loader : typing.Callable
    sheriff_loader : typing.Callable
    saloon_loader : typing.Callable
    cinema_loader : typing.Callable
    _history = []
    def _save_to_feed(self,building_name:str,action:str = "load"):
        self._history.append(f'Querried {building_name} in order to {action} at {datetime.datetime.now()}')
    def get(self,building_name:str) -> Building_preloader:
        getattr(self,building_name).load()
    @property
    def history(self):
        return self._history
    def print_history(self,number:int = None):
        if number is not None:
            print(self._history[(lambda x : - min( x , len(self._history ))) (number)::])
        else:
            print(self._history)
class CityNotFoundError(Exception):
    pass
def load_town_buildings(handler : requests_handler,work_manager : Work_manager ,player_data:Player_data, coords : tuple[int,int]) -> Town_buildings:
    
    response = handler.post(window="town",action="get_town",action_name="mode",payload={"x":f"{coords[0]}","y":f"{coords[1]}"})
    
    if response['error'] :
        raise CityNotFoundError(f"Couldn't find the city at the coords ( {coords[0]} , {coords[1]} ) !")
    
    
    town_building_data = response['allBuildings']
    town_id = response['town_id']

    return Town_buildings(
                    cityhall = City_hall_building_preloader(level=town_building_data['cityhall']['stage'],
                                                            town_id = town_id,
                                                            handler = handler
                                                            ),
                    market = Token_preloader(),
                    tenement = Token_preloader() ,
                    bank =  Bank_building_preloader(level=town_building_data['bank']['stage'],
                                                    town_id = town_id,
                                                    handler=handler),
                    hotel = Hotel_building_preloader(level = town_building_data['hotel']['stage'],
                                                     town_id = town_id,
                                                     handler = handler,
                                                     work_manager = work_manager,
                                                     player_data= player_data
                                                     ) ,
                    gunsmith = Shop_building_preloader(town_id = town_id ,
                                                       shop_type='gunsmith_building' ,
                                                       level = town_building_data['gunsmith']['stage'],
                                                       handler= handler) ,
                    tailor = Shop_building_preloader(town_id = town_id ,
                                                     shop_type='tailor_building' , 
                                                     level = town_building_data['tailor']['stage'],
                                                     handler= handler) ,
                    general = Shop_building_preloader(town_id = town_id ,
                                                      shop_type='general_building' ,
                                                      level = town_building_data['general']['stage'],
                                                      handler= handler) ,
                    mortician = Mortician_building_preloader(
                                                            level = town_building_data['mortician']['stage'],
                                                            handler = handler ,
                                                            town_id = town_id) ,
                    church = Church_building_preloader(
                                                        level = town_building_data['church']['stage'] ,
                                                        handler = handler,
                                                        town_id = town_id,
                                                        work_manager = work_manager ) ,
                    sheriff = Token_preloader() ,
                    saloon = Token_preloader() ,
                    cinema = Cinema_building_preloader(level=1,town_id= town_id,handler = requests_handler)                         
                    )
