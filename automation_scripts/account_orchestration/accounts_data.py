import typing
import concurrent.futures

from the_west_inner.login import Game_login
from the_west_inner.game_classes import Game_classes

from the_west_inner.item_set_general import Item_sets,get_item_sets
from the_west_inner.bag import Bag
from the_west_inner.currency import Currency
from the_west_inner.equipment import Equipment
from connection_sessions.standard_request_session import StandardRequestsSession
from the_west_inner.map import MapLoader

ItemIDType = int
ExchangeDictType = dict[ItemIDType, typing.Optional[int]]
ScriptType = typing.Callable[[Game_classes ],None] | typing.Callable[[Game_classes,Game_login],None]

def update_dict(target_dict : ExchangeDictType , extension_dict : ExchangeDictType):
    
    for item_id , item_number in extension_dict.items():
        
        if item_id in target_dict:
            target_dict[item_id] += item_number
        else:
            target_dict[item_id] = item_number
    
    return target_dict


SessionBuilderFuncType = typing.Callable[[Game_login],StandardRequestsSession]
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
    
    def unload(self) -> None:
        
        self.bag = None
        self.currency = None
        self.current_equipment = None
        
    def _login_by_func(self , 
                       session_builder_func : SessionBuilderFuncType| None = None) -> Game_login:
        
        if session_builder_func is None :
            return self.login
        
        return Game_login(
            player_name = self.login.player_name,
            player_password= self.login.player_password,
            world_id = self.login.world_id,
            session_builder_func = session_builder_func
        )
        
        
    def load(self,
             session_builder_func : SessionBuilderFuncType| None = None
             ) -> typing.Generator[tuple[Game_classes,Game_login],None,None]:
        
        login = self._login_by_func(session_builder_func = session_builder_func)
        game_classes = login.login()
        
        yield game_classes , login

        self.bag = game_classes.bag
        self.currency = game_classes.currency
        if game_classes.currency.cash is None:
            town_list = MapLoader(
                handler= game_classes.handler,
                player_data = game_classes.player_data,
                work_list = game_classes.work_list
            ).get_town_list()
            game_classes.currency.update_raw(town_list= town_list,
                                             requests_handler= game_classes.handler,
                                             player_data= game_classes.player_data
                                             )
        
        self.current_equipment = game_classes.equipment_manager.current_equipment
        if isinstance(game_classes.handler.session, StandardRequestsSession):
            game_classes.handler.session.force_change_connection()
    
    def get_item_number(self, item_id : int , count_equipped : bool = True) -> int:
        additional = 0
        if item_id in self.current_equipment and count_equipped:
            additional = 1
        return self.bag[item_id] + additional
    def get_items_by_item_list(self, item_id_list : list[int], count_equipped : bool = True) -> ExchangeDictType :
        
        return {x : self.get_item_number(item_id = x,count_equipped= count_equipped) for x in item_id_list 
                                    if self.get_item_number(item_id = x , count_equipped= count_equipped) != 0}
        
    def get_money(self ) -> int:
        
        return self.currency.total_money


class CompleteAccountData:
    def __init__(self , accounts : list[Game_login]):
        
        if len({x.world_id for x in accounts}) > 1:
            raise ValueError(f'CompleteAccountData does not support multi world comparisons !')
        self.accounts : list[AccountData] = [AccountData(login=x) for x in accounts]
        self._sets : None | Item_sets = None
    
    def is_loaded(self) -> bool:
        
        return all([x.is_loaded for x in self.accounts])
    
    def unload_all(self) -> None:
        
        for account in self.accounts  :
            account.unload()
    
    def _load_sets(self , game_classes : Game_classes):
        
        if self._sets is None:
            sets = get_item_sets(requests_handler = game_classes.handler)
            self._sets = sets
    def _load_account_async(self,
                            account_data: AccountData,
                            session_builder_func: SessionBuilderFuncType,
                            callback_func : ScriptType | None = None
                            ):
        """
        Helper function to load an account asynchronously. 
        """
        load_generator = account_data.load(session_builder_func=session_builder_func)
        
        game_classes , login = next(load_generator)
            
        self._load_sets(game_classes = game_classes)
        
        #consume the rest of the generator
        for _ in load_generator:
            pass
        
        callback_func(game_classes,login)
    def load_all(self, 
                session_builder_func: SessionBuilderFuncType | None = None,
                 callback_func : ScriptType | None = None):
        
        for account_data in self.accounts:
            
            self._load_account_async(
                account_data= account_data,
                session_builder_func=session_builder_func,
                callback_func= callback_func
            )
    def _load_all_async_recursive(self,
                                session_builder_func: SessionBuilderFuncType,
                                callback_func : ScriptType | None = None
                                ):
        """
        Recursively loads accounts asynchronously until all are loaded.
        """
        # Check which accounts are not yet loaded
        unloaded_accounts = [account for account in self.accounts if not account.is_loaded]

        if not unloaded_accounts:
            # All accounts are loaded, end recursion
            return

        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Create a list of future tasks for each unloaded account
            futures = [
                executor.submit(self._load_account_async, account_data, session_builder_func , callback_func)
                for account_data in unloaded_accounts
            ]
            # Wait for all futures to complete
            done, not_done = concurrent.futures.wait(futures)

            # Check for exceptions and raise them
            for future in done:
                future.result()
            
        
        # Recurse until all accounts are loaded
        self._load_all_async_recursive(session_builder_func=session_builder_func,
                                       callback_func= callback_func
                                       )

    def load_all_async(self,
                    session_builder_func: SessionBuilderFuncType,
                    callback_func : ScriptType | None = None
                    ):
        """
        Public method to initiate recursive async loading.
        """
        self._load_all_async_recursive(session_builder_func = session_builder_func,
                                       callback_func = callback_func
                                       )
    def get_money(self) -> int:
        return sum([x.get_money() for x in self.accounts])
    
    def get_account_money(self) -> typing.Generator[tuple[AccountData,int] , None ,None]:
        
        for account in self.accounts:
            
            yield account , account.get_money()
    
    def get_number_of_items(self, item_id : int) -> int:
        
        return sum([x.get_item_number(item_id = item_id) for x in self.accounts])
    
    def __iter__(self) -> typing.Iterator[AccountData] :
        
        return iter(self.accounts)
    
    def get_by_id_list(self, id_list : list[int] , count_equipped : bool = True) -> typing.Generator[tuple[AccountData, ExchangeDictType],None ,None]:
        
        for account in self.accounts:
            
            yield account ,account.get_items_by_item_list(item_id_list = id_list,count_equipped= count_equipped)
    
    def get_complete_dict_by_id_list(self , id_list : list[int]) :
        complete_dict = {}
        
        for _ , exchange_dict in self.get_by_id_list(id_list = id_list):
            
            complete_dict = update_dict(target_dict = complete_dict ,
                                        extension_dict = exchange_dict
                                        )
        
        return complete_dict
    def _get_set_item_list_by_id(self , example_item_id : int) -> list[int]:
        
        item_set = self._sets.get_set_by_example_item(item_id = example_item_id)
        
        if item_set is None:
            return []
        
        return item_set.list_items
        
    def get_all_set_items_by_item_ids(self , id_list : list[int] , count_equipped : bool = True):
        
        set_item_ids = set()
        
        for item_id in id_list:
            
            result_list = self._get_set_item_list_by_id(example_item_id=item_id)
            set_item_ids.update(result_list)
        
        return self.get_by_id_list(id_list = set_item_ids ,count_equipped=count_equipped)
    
    