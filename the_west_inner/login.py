import requests
from urllib.parse import urlparse
import json
import typing

from game_classes import Game_classes
from requests_handler import requests_handler
from movement import Game_data
from player_data import Player_data
from init_data import return_h, return_premium_data, return_bag, return_work_list, return_cooldown , return_wear_data , return_buff_data
from task_queue import TaskQueue
from premium import Premium
from misc_scripts import server_time
from work_list import Work_list
from items import Items,return_items
from crafting import Crafting_table,Crafting
from work_manager import Work_manager
from consumable import Consumable_handler,Cooldown
from bag import Bag
from skills import read_skill
from equipment import create_initial_equipment , Equipment_manager
from buffs import build_buff_list

def game_instance(player_name:str,player_password:str,world_id:str) -> Game_classes:
    """
    Initializes a Game_instance object by making HTTP requests to the "The West" website using the requests library,
    and parsing the responses to gather information about the player's game state.

    Arguments:
    player_name (str): the name of the player
    player_password (str): the password of the player
    world_id (str): the ID of the world in which the player is playing

    Returns:
    Game_classes: an object containing all of the game state data, including instances of the following classes:
        - Game_data
        - Player_data
        - TaskQueue
        - Premium
        - Work_list
        - Items
        - Crafting_table
        - Crafting
        - Bag
        - Cooldown
        - Consumable_handler
        - Work_manager
        - Equipment_manager
    """
    with requests.Session() as s:
        # Set the User-Agent header
        s.headers = {"User-Agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}

        # Send a POST request to the "check_login" endpoint with the player name and password
        password_id  = s.post("https://www.the-west.ro//index.php?ajax=check_login&locale=ro_RO", data ={"name": f"{player_name}","password": f"{player_password}"}).text

        # Parse the response as JSON
        password_json = json.loads(password_id)

        # Extract the player_id and password_hash from the JSON response
        player_id = password_json["player_id"]
        password_hash = password_json["password"]

        # Send a POST request to the "login" endpoint with the world_id, player_id, and password_hash
        a = s.post("https://www.the-west.ro/?action=login", data={"world_id": f"{world_id}","player_id": f"{player_id}","password": f"{password_hash}","set_cookie": ""},allow_redirects=False)

        # Send another POST request to the URL specified in the Location header of the previous response
        b = s.post(f"{a.headers['Location']}",allow_redirects=False)

        # Send a GET request to the URL specified in the Location header of the previous response
        c = s.get(f"{b.headers['Location']}",allow_redirects=False)

        # Set the X-Requested-With header to "XMLHttpRequest"
        s.headers['X-Requested-With'] = 'XMLHttpRequest'

        # Extract the active game URL from the previous response
        active_game_url = c.url

        # Send a POST request to the "ntp.php" endpoint
        d = s.post(urlparse(active_game_url)._replace(path="ntp.php").geturl(),allow_redirects=False)
        # Send a GET request to the "task" endpoint
        e = s.get(urlparse(active_game_url)._replace(query="window=task").geturl(),allow_redirects=False)

        # Create a "handler" object using the requests.Session object and the active_game_url
        driver = requests_handler(s,active_game_url,return_h(c))

        # Create a Game_data object with a default game_travel_speed of 0.9
        game_data = Game_data(game_travel_speed=0.9)

        # Create a Player_data object with the player_id, player_name, and game_data
        player_data = Player_data(id=player_id,
                    x= 0,
                    y= 0,
                    name= player_name,
                    game_data=game_data,
                    character_movement = 0,
                    hp=0,
                    hp_max=0,
                    energy=0,
                    energy_max=0,
                    level=0,
                    experience=0
                    )

        # Update the character_movement attribute of the Player_data object using the "handler" object
        player_data.update_character_movement(driver)

        # Update the character variables (hp, energy, level, etc.) of the Player_data object using the "handler" object
        player_data.update_character_variables(driver)

        # Update the location of the Player_data object using the "handler" object
        player_data.update_location(driver)

        # Create a TaskQueue object using the "handler" object and the Player_data object
        task_queue = TaskQueue(handler=driver,
                            player_data=player_data
                            )

        # Create a Premium object using the data from the "c" response and the server time from the "handler" object
        premium = Premium(return_premium_data(c.text),server_time(handler=driver))

        # Create a Work_list object using the data from the "c" response
        work_list = Work_list(return_work_list(c.text))

        # Create an Items object using the "handler" object
        items = Items(return_items(driver))

        # Create a Crafting_table object using the Items object
        crafting_table = Crafting_table(items)

        # Create a Crafting object using the Crafting_table object and the "handler" object
        player_crafting = Crafting(crafting_table=crafting_table,handler=driver)

        # Create a Bag object using the data from the "c" response
        bag = Bag(return_bag(c.text))

        # Create a Cooldown object using the data from the "c" response and the "handler" object
        cooldown = Cooldown(handler=driver,cooldown_date= return_cooldown(c.text))

        # Create a Consumable_handler object using the "handler" object, Bag object, and Cooldown object
        consumable_handler = Consumable_handler(
                            handler= driver ,
                            bag= bag ,
                            cooldown= cooldown
                            )
        # Create a Work_manager object using the "handler" object, TaskQueue object, Premium object, and Player_data object
        work_manager = Work_manager(handler = driver,
                                    task_queue= task_queue,
                                    premium= premium ,
                                    player_data = player_data
                                    )

        # Read the player's skills using the "handler" object
        skills = read_skill(handler= driver)

        # Create a list of the player's current equipment using the data from the "c" response and the Items object
        current_equipment = create_initial_equipment( item_list= return_wear_data(c.text) , items= items)

        # Create an Equipment_manager object using the current equipment, Bag object, Items object, and skills
        equipment_manager = Equipment_manager(
            current_equipment= current_equipment ,
            bag= bag ,
            items= items ,
            skills= skills
        )
        
        #Extract the dict associated with the player's buff(bonus effects)
        buff_dict = return_buff_data(initialization_html = c.text)
        
        #Create a Buff_list object to handle the player's buffs
        buff_list = build_buff_list(input_dict = buff_dict)

        # Create a Game_classes object containing all of the game state data
        game_classes = Game_classes(
                        handler = driver , 
                        game_data = game_data ,
                        player_data = player_data ,
                        task_queue = task_queue ,
                        premium = premium ,
                        work_list = work_list ,
                        items = items ,
                        crafting_table = crafting_table ,
                        player_crafting = player_crafting ,
                        bag = bag ,
                        cooldown = cooldown ,
                        buff_list = buff_list ,
                        work_manager = work_manager ,
                        consumable_handler= consumable_handler ,
                        equipment_manager= equipment_manager
                        
        )
        
        # Return the Game_classes object
        return game_classes

def game_classes_builder(active_world_url : str, game_requests_session: requests.Session , game_raw_data : requests.Response ,player_name : str , player_id : int) -> Game_classes :
        # Create a "handler" object using the requests.Session object and the active_game_url
        driver = requests_handler(game_requests_session ,active_world_url, return_h(game_raw_data))

        # Create a Game_data object with a default game_travel_speed of 0.9
        game_data = Game_data(game_travel_speed=0.9)

        # Create a Player_data object with the player_id, player_name, and game_data
        player_data = Player_data(id=player_id,
                    x= 0,
                    y= 0,
                    name= player_name,
                    game_data=game_data,
                    character_movement = 0,
                    hp=0,
                    hp_max=0,
                    energy=0,
                    energy_max=0,
                    level=0,
                    experience=0
                    )

        # Update the character_movement attribute of the Player_data object using the "handler" object
        player_data.update_character_movement(driver)

        # Update the character variables (hp, energy, level, etc.) of the Player_data object using the "handler" object
        player_data.update_character_variables(driver)

        # Update the location of the Player_data object using the "handler" object
        player_data.update_location(driver)

        # Create a TaskQueue object using the "handler" object and the Player_data object
        task_queue = TaskQueue(handler=driver,
                            player_data=player_data
                            )

        # Create a Premium object using the data from the "game_raw_data" response and the server time from the "handler" object
        premium = Premium(return_premium_data(game_raw_data.text),server_time(handler=driver))

        # Create a Work_list object using the data from the "game_raw_data" response
        work_list = Work_list(return_work_list(game_raw_data.text))

        # Create an Items object using the "handler" object
        items = Items(return_items(driver))

        # Create a Crafting_table object using the Items object
        crafting_table = Crafting_table(items)

        # Create a Crafting object using the Crafting_table object and the "handler" object
        if player_data.profession_id != -1:
            player_crafting = Crafting(crafting_table=crafting_table,handler=driver)
        else:
            player_crafting = None

        # Create a Bag object using the data from the "game_raw_data" response
        bag = Bag(return_bag(game_raw_data.text))

        # Create a Cooldown object using the data from the "game_raw_data" response and the "handler" object
        cooldown = Cooldown(handler=driver,cooldown_date= return_cooldown(game_raw_data.text))

        # Create a Consumable_handler object using the "handler" object, Bag object, and Cooldown object
        consumable_handler = Consumable_handler(
                            handler= driver ,
                            bag= bag ,
                            cooldown= cooldown
                            )
        # Create a Work_manager object using the "handler" object, TaskQueue object, Premium object, and Player_data object
        work_manager = Work_manager(handler = driver,
                                    task_queue= task_queue,
                                    premium= premium ,
                                    player_data = player_data
                                    )

        # Read the player's skills using the "handler" object
        skills = read_skill(handler= driver)

        # Create a list of the player's current equipment using the data from the "game_raw_data" response and the Items object
        current_equipment = create_initial_equipment( item_list= return_wear_data(game_raw_data.text) , items= items)

        # Create an Equipment_manager object using the current equipment, Bag object, Items object, and skills
        equipment_manager = Equipment_manager(
            current_equipment= current_equipment ,
            bag= bag ,
            items= items ,
            skills= skills
        )                
        #Extract the dict associated with the player's buff(bonus effects)
        buff_dict = return_buff_data(initialization_html = game_raw_data.text)
        #Create a Buff_list object to handle the player's buffs
        buff_list = build_buff_list(input_dict = buff_dict)

        # Create a Game_classes object containing all of the game state data
        game_classes = Game_classes(
                        handler = driver , 
                        game_data = game_data ,
                        player_data = player_data ,
                        task_queue = task_queue ,
                        premium = premium ,
                        work_list = work_list ,
                        items = items ,
                        crafting_table = crafting_table ,
                        player_crafting = player_crafting ,
                        bag = bag ,
                        cooldown = cooldown ,
                        buff_list = buff_list ,
                        work_manager = work_manager ,
                        consumable_handler= consumable_handler ,
                        equipment_manager= equipment_manager
                        
        )
        
        # Return the Game_classes object
        return game_classes


class Game_login():
    def __init__(self,player_name:str , player_password:str, world_id : typing.Union[str,int] , use_tor_flag : bool = False):
        self.player_name = player_name 
        self.player_password = player_password
        self.world_id = world_id
        self.session = self._create_session()
        self.url = ""
        self.game_html = None
    def _set_url(self,url:str)->None:
        self.url = url
    def _create_session (self , use_tor_flag : bool = False) -> requests.Session :
        if use_tor_flag:
            
            pass
            
        with requests.Session() as session:
            # Set the User-Agent header
            session.headers = {"User-Agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}
            
            return session
    def _login_account(self) -> typing.Tuple[str,str]:    
        # Send a POST request to the "check_login" endpoint with the player name and password
        password_id  = self.session.post("https://www.the-west.ro//index.php?ajax=check_login&locale=ro_RO", 
                                data ={"name": f"{self.player_name}","password": f"{self.player_password}"}).text

        # Parse the response as JSON
        password_json = json.loads(password_id)

        # Extract the player_id and password_hash from the JSON response
        player_id = password_json["player_id"]
        password_hash = password_json["password"]
        
        return player_id , password_hash
    def _select_world(self,player_id :str , password_hash:str) -> str:
        # Send a POST request to the "login" endpoint with the world_id, player_id, and password_hash
        login_response = self.session.post("https://www.the-west.ro/?action=login", 
                              data={"world_id": f"{self.world_id}","player_id": f"{player_id}","password": f"{password_hash}","set_cookie": ""},allow_redirects=False)

        # Send another POST request to the URL specified in the Location header of the previous response
        game_page_response = self.session.post(f"{login_response.headers['Location']}",allow_redirects=False)

        # Send a GET request to the URL specified in the Location header of the previous response
        game_state_response = self.session.get(f"{game_page_response.headers['Location']}",allow_redirects=False)

        # Set the X-Requested-With header to "XMLHttpRequest"
        self.session.headers['X-Requested-With'] = 'XMLHttpRequest'

        # Extract the active game URL from the previous response
        active_game_url = game_state_response.url
        # Set the active URL to a new game-world specific one 
        self._set_url(url=active_game_url)
        
        #The next 2 requests are not actually used anywhere but are done so the game does not detect a bot
        # Send a POST request to the "ntp.php" endpoint
        self.session.post(urlparse(active_game_url)._replace(path="ntp.php").geturl(),allow_redirects=False)
        # Send a GET request to the "task" endpoint
        self.session.get(urlparse(active_game_url)._replace(query="window=task").geturl(),allow_redirects=False)
        
                
        return game_state_response
    def login(self ) -> Game_classes :
        player_id , password_hash = self._login_account()
        game_raw_data = self._select_world(player_id=player_id,
                                           password_hash= password_hash
                                           )
        self.game_html = game_raw_data.text
        return game_classes_builder(
            active_world_url= self.url ,
            game_requests_session= self.session ,
            game_raw_data= game_raw_data ,
            player_name= self.player_name ,
            player_id= player_id )