import typing
import concurrent.futures


from automation_scripts.account_orchestration.accounts_data import CompleteAccountData , AccountData , ScriptType
from connection_sessions.standard_request_session import StandardRequestsSession
from the_west_inner.game_classes import Game_classes
from the_west_inner.login import Game_login

SessionBuilderFuncType = typing.Callable[[Game_login],StandardRequestsSession]

class AccountDataScriptManager:
    
    def __init__(self , account_data : CompleteAccountData ):
        
        self.account_data = account_data
        self.available_dict = {(x.login.player_name,x.login.world_id) : x for x in account_data.accounts}
        self.unavailable_account : set[AccountData] = set()
    
    
    def _get_account_login(self, 
                           account_data : AccountData ,
                           session_builder_func : SessionBuilderFuncType | None = None ) -> Game_login:

        
        if session_builder_func is None:
            return account_data.login
        
        return Game_login(
            player_name = account_data.login.player_name,
            player_password= account_data.login.player_password,
            world_id = account_data.login.world_id,
            session_builder_func = session_builder_func
        )
    
    def _execute_script(self,
                        account_data : AccountData ,
                        account_script : ScriptType,
                        session_builder_func : SessionBuilderFuncType | None = None):
        
        login = self._get_account_login(account_data = account_data , session_builder_func = session_builder_func)
        
        account_script(login)
        
    def async_execute(self ,
                      account_script : ScriptType ,
                      session_builder_func : SessionBuilderFuncType | None = None
                      ) :

        self.account_data.load_all_async(
            session_builder_func = session_builder_func,
            callback_func = account_script
        )
        self.account_data.unload_all()
    
    def execute(self ,
                account_script : ScriptType,
                session_builder_func : SessionBuilderFuncType | None = None
                ):
        
        self.account_data.load_all(
            session_builder_func=session_builder_func,
            callback_func = account_script
        )
        self.account_data.unload_all()