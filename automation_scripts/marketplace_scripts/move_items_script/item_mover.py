from typing import Dict, Optional

from connection_sessions.standard_request_session import StandardRequestsSession

from the_west_inner.login import Game_login, Game_classes
from the_west_inner.map import MapLoader
from the_west_inner.marketplace import Marketplace_managers, build_marketplace_managers

ItemIDType = int
ExchangeDictType = Dict[ItemIDType, Optional[int]]


class ItemMoverAgent:
    """
    Class to represent an agent that can move items within the game.
    """

    def __init__(self, game_classes: Game_classes, marketplace_managers: Marketplace_managers, exchange_price: int):
        """
        Initializes an ItemMoverAgent with the provided game classes, marketplace managers, and exchange price.

        Args:
            game_classes (Game_classes): The game classes instance.
            marketplace_managers (Marketplace_managers): The marketplace managers instance.
            exchange_price (int): The price at which items will be exchanged.
        """
        self.game_classes = game_classes
        self._player_id = game_classes.player_data.id
        self.marketplace_managers = marketplace_managers
        self.exchange_price = exchange_price
    
    @property
    def player_id(self) -> int:
        """
        Returns the player ID.

        Returns:
            int: Player ID.
        """
        return self._player_id

    @property
    def money(self) -> int:
        """
        Returns the total money the player has.

        Returns:
            int: Total money.
        """
        return self.game_classes.currency.total_money

    @property
    def has_money(self) -> bool:
        """
        Checks if the player has enough money for an exchange.

        Returns:
            bool: True if the player has enough money, False otherwise.
        """

        return self.money >= self.exchange_price
    
    def get_item_number(self, item_id: int) -> int:
        """
        Gets the number of a specific item in the player's bag.

        Args:
            item_id (int): The item ID.

        Returns:
            int: The number of items.
        """
        item_num = self.game_classes.bag[item_id]
        return item_num + 1 if item_id in self.game_classes.equipment_manager.current_equipment else item_num
    
    def _free_task_queue(self) -> bool:
        """
        Frees up the task queue by cancelling tasks.

        Returns:
            bool: True if successful, False otherwise.
        """
        task_queue = self.game_classes.task_queue
        return task_queue.tasks.cancel()
    
    def empty_task_queue(self):
        """
        Empties the task queue if any tasks exist.

        Returns:
            None
        """
        if self.game_classes.task_queue.get_tasks_number() != 0:
            self._free_task_queue()
    
    def get_map_position(self) -> tuple[int, int]:
        """
        Gets the player's current position on the map.

        Returns:
            tuple[int, int]: The (x, y) position on the map.
        """
        return (self.game_classes.player_data.x, self.game_classes.player_data.y)
    
    def move_to_town(self):
        """
        Moves the player to the closest town.
        """
        self.game_classes.movement_manager.move_to_closest_town()
    
    def buy_from_marketplace(self, item_id: int, player_id: int) -> bool:
        """
        Buys an item from the marketplace.

        Args:
            item_id (int): The item ID.
            player_id (int): The player ID to buy from.

        Returns:
            bool: True if the purchase was successful, False otherwise.
        """
        return self.marketplace_managers.marketplace_buy_manager.buy_item_from_player_max_price(
            item_id=item_id,
            player_id=player_id,
            max_price=self.exchange_price
        )
    
    def sell_item(self, item_id: int, number: int = 1 , is_token :bool = False , token_min_price : int = 50_000) -> bool:
        """
        Sells an item in the nearest town.

        Args:
            item_id (int): The item ID.
            number (int): The number of items to sell.

        Returns:
            bool: True if the sale was successful, False otherwise.
        """
        if self.game_classes.bag[item_id] + 1 == number and item_id in self.game_classes.equipment_manager.current_equipment:
            
            self.move_to_town()
            self.game_classes.equipment_manager.unequip_item(
                item_id = item_id,
                handler=self.game_classes.handler
            )
        
        if is_token:
            return self.marketplace_managers.marketplace_sell_manager.sell_in_nearest_town(
                item_id=item_id,
                number_of_items=number,
                unitary_price=int(self.exchange_price / number),
                min_price= token_min_price
                
            )
        
        return self.marketplace_managers.marketplace_sell_manager.sell_in_nearest_town(
            item_id=item_id,
            number_of_items=number,
            unitary_price=int(self.exchange_price / number),
            minimise_tax_flag=True
        )
    
    def collect_sold(self):
        """
        Collects all sold items from the marketplace.
        """
        self.marketplace_managers.marketplace_pickup_manager.fetch_all_sold()
    
    def collect_bought(self):
        """
        Collects all bought items from the marketplace.
        """
        self.marketplace_managers.marketplace_pickup_manager.fetch_all_bought()
    
    def refresh_connection(self):
        
        if isinstance(self.game_classes.handler.session , StandardRequestsSession):
            
            self.game_classes.handler.session.force_change_connection()


class ItemMover:
    """
    Class to manage the exchange of items between two ItemMoverAgents.
    """

    def __init__(self, 
                 target_item_mover: ItemMoverAgent, 
                 item_mover_donator: ItemMoverAgent,
                 required_item_list: ExchangeDictType,
                 exchange_token_item: int):
        """
        Initializes an ItemMover with the provided target agent, donator agent, required items, and exchange token.

        Args:
            target_item_mover (ItemMoverAgent): The agent receiving the items.
            item_mover_donator (ItemMoverAgent): The agent donating the items.
            required_item_list (ExchangeDictType): The list of required items and their quantities.
            exchange_token_item (int): The item used as an exchange token.
        """
        self.target_item_mover = target_item_mover
        self.item_mover_donator = item_mover_donator
        self.required_item_list = required_item_list
        self.exchange_token_item = exchange_token_item
    
    def _exchange_simple(self,
                         seller_agent: ItemMoverAgent,
                         buyer_agent: ItemMoverAgent,
                         item_id: int,
                         item_number: int):
        """
        Handles a simple item exchange between two agents.

        Args:
            seller_agent (ItemMoverAgent): The agent selling the item.
            buyer_agent (ItemMoverAgent): The agent buying the item.
            item_id (int): The item ID.
            item_number (int): The number of items to exchange.
        """
        
        if item_id == self.exchange_token_item:
            seller_agent.sell_item(item_id=item_id, number=item_number, is_token=True)
        else:
            seller_agent.sell_item(item_id=item_id, number=item_number)
        buyer_agent.buy_from_marketplace(item_id=item_id, player_id=seller_agent.player_id)
        seller_agent.collect_sold()
        
    def exchange_item(self, item_id: int, item_number: int):
        """
        Exchanges a specific item between the donator and the target mover.

        Args:
            item_id (int): The item ID.
            item_number (int): The number of items to exchange.

        Raises:
            ValueError: If either agent does not have enough money.
        """
        if not self.target_item_mover.has_money:
            raise ValueError("Target mover doesn't have enough money")

        self._exchange_simple(
            seller_agent=self.item_mover_donator,
            buyer_agent=self.target_item_mover,
            item_id=item_id,
            item_number=item_number
        )
        
        if not self.item_mover_donator.has_money:
            raise ValueError("Donator doesn't have enough money")
        self._exchange_simple(
            seller_agent=self.target_item_mover,
            buyer_agent=self.item_mover_donator,
            item_id=self.exchange_token_item,
            item_number=1
        )
        
    def exchange_all(self):
        """
        Exchanges all required items between the donator and the target mover.
        """
        for item_id, number in self.required_item_list.items():
            if number is None:
                number = self.item_mover_donator.get_item_number(item_id=item_id)
            if number == 0:
                print(f'You have no item: {item_id}!')
                continue
            
            self.exchange_item(item_id=item_id, item_number=number)
        
        self.target_item_mover.refresh_connection()
        self.item_mover_donator.refresh_connection()
    def collect_exchanged_items(self):
        """
        Collects all items bought by the target mover.
        """
        self.target_item_mover.collect_bought()


class MoneyMover:
    """
    Class to manage the exchange of money between two ItemMoverAgents.
    """

    def __init__(self, 
                 target_item_mover: ItemMoverAgent, 
                 item_mover_donator: ItemMoverAgent,
                 exchange_token_item: int):
        """
        Initializes a MoneyMover with the provided target agent, donator agent, and exchange token.

        Args:
            target_item_mover (ItemMoverAgent): The agent receiving the money.
            item_mover_donator (ItemMoverAgent): The agent donating the money.
            exchange_token_item (int): The item used as an exchange token.
        """
        self.target_item_mover = target_item_mover
        self.item_mover_donor = item_mover_donator
        self.exchange_token_item = exchange_token_item
    
    def send_money(self) -> bool:
        """
        Sends money from the donator to the target mover using an exchange token item.

        Returns:
            bool: True if the transaction was successful, False otherwise.
        """
        self.target_item_mover.sell_item(
            item_id=self.exchange_token_item,
            number=1
        )
        
        buy_bool = self.item_mover_donor.buy_from_marketplace(
            item_id=self.exchange_token_item,
            player_id=self.target_item_mover.player_id
        )
        
        self.target_item_mover.collect_sold()
        
        self.target_item_mover.refresh_connection()
        self.item_mover_donor.refresh_connection()

        return buy_bool
        


class ItemMoverBuilder:
    """
    Builder class for creating an ItemMover or MoneyMover instance.
    """
    
    def __init__(self, 
                 login_target: Game_login, 
                 login_origin: Game_login, 
                 exchange_token_item: int,
                 exchange_value: int):
        """
        Initializes an ItemMoverBuilder with the provided login details, exchange token, and value.

        Args:
            login_target (Game_login): The login instance for the target player.
            login_origin (Game_login): The login instance for the origin player.
            exchange_token_item (int): The item used as an exchange token.
            exchange_value (int): The value of the exchange.
        """
        self.login_target = login_target
        self.login_origin = login_origin
        self.exchange_token_item = exchange_token_item
        self.exchange_value = exchange_value

    def transaction_number(self, required_item_list: ExchangeDictType|None = None) -> int:
        """
        Calculates the total number of transactions required.

        Args:
            required_item_list (ExchangeDictType): The list of required items and their quantities.

        Returns:
            int: Total number of transactions.
        """
        return len(required_item_list) if required_item_list else 1
    
    def _make_agent(self, game_login: Game_login) -> ItemMoverAgent:
        """
        Creates an ItemMoverAgent for a given game login.

        Args:
            game_login (Game_login): The game login instance.

        Returns:
            ItemMoverAgent: The created agent.
        """
        game_classes = game_login.login()
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
        marketplace_managers = build_marketplace_managers(
            handler=game_classes.handler,
            items=game_classes.items,
            currency=game_classes.currency,
            movement_manager=game_classes.movement_manager,
            bag=game_classes.bag,
            player_data=game_classes.player_data
        )
        
        agent = ItemMoverAgent(
            game_classes=game_classes,
            marketplace_managers=marketplace_managers,
            exchange_price=self.exchange_value
        )
        agent.empty_task_queue()
        
        return agent

    def _make_target_agent(self, 
                           requirement_item_list: Optional[ExchangeDictType] = None ,
                           cash_flag : bool = False
                           ) -> ItemMoverAgent:
        """
        Creates the target ItemMoverAgent.

        Args:
            requirement_item_list (Optional[ExchangeDictType]): The list of required items and their quantities.

        Returns:
            ItemMoverAgent: The target agent.

        Raises:
            ValueError: If the target agent does not have enough money or token items.
        """
        agent = self._make_agent(game_login=self.login_target)
        
        if not cash_flag and not agent.has_money:
            raise ValueError('Target agent does not have enough money to do the transactions!')
        
        if agent.get_item_number(item_id=self.exchange_token_item) < self.transaction_number(
                required_item_list=requirement_item_list ):
            raise ValueError('Target agent does not have enough token items for transaction!')
        
        return agent

    def _make_donator_agent(self, 
                            requirement_item_list: Optional[ExchangeDictType] = None ,
                           cash_flag : bool = False) -> ItemMoverAgent:
        """
        Creates the donator ItemMoverAgent.

        Args:
            requirement_item_list (Optional[ExchangeDictType]): The list of required items and their quantities.

        Returns:
            ItemMoverAgent: The donator agent.

        Raises:
            ValueError: If the donator agent does not have enough items or money.
        """
        if requirement_item_list is None:
            requirement_item_list = {}
        agent = self._make_agent(game_login=self.login_origin)
        
        items_not_found = [item_id for item_id, item_number in requirement_item_list.items()
                           if item_number is not None and agent.get_item_number(item_id=item_id) < item_number]
        
        if cash_flag and agent.money < self.exchange_value:
            raise ValueError('You do not have enough money to make the monetary exchange!')
        
        if items_not_found:
            raise ValueError(f'Could not start exchanging because of limited items: {items_not_found}')
        
        return agent
    
    def build_item_mover(self, requirement_item_list: ExchangeDictType) -> ItemMover:
        """
        Builds and returns an ItemMover instance.

        Args:
            requirement_item_list (ExchangeDictType): The list of required items and their quantities.

        Returns:
            ItemMover: The created ItemMover instance.
        """
        return ItemMover(
            target_item_mover=self._make_target_agent(requirement_item_list=requirement_item_list),
            item_mover_donator=self._make_donator_agent(requirement_item_list=requirement_item_list),
            required_item_list=requirement_item_list,
            exchange_token_item=self.exchange_token_item
        )
    
    def build_money_mover(self) -> MoneyMover:
        """
        Builds and returns a MoneyMover instance.

        Returns:
            MoneyMover: The created MoneyMover instance.
        """
        return MoneyMover(
            target_item_mover=self._make_target_agent(cash_flag=True),
            item_mover_donator=self._make_donator_agent(cash_flag=True),
            exchange_token_item=self.exchange_token_item
        )
    