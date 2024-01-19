import typing
from requests_handler import requests_handler
from movement_manager import MovementManager
from marketplace_buy import Marketplace_offer,Marketplace_offer_list
from items import Items
from currency import Currency
from bag import Bag


class MarketplacePickupManager:
    """
    A class representing a manager for picking up items from the marketplace in a game.
    """

    def __init__(self,
                 handler: requests_handler,
                 movement_manager: MovementManager,
                 items: Items,
                 bag: Bag,
                 currency: Currency):
        """
        Initializes the MarketplacePickupManager with required components.

        Args:
            handler (requests_handler): The request handler for making marketplace-related requests.
            movement_manager (MovementManager): The manager for handling movement in the game.
            items (Items): The items available in the game.
            bag (Bag): The bag to store collected items (player's inventory).
            currency (Currency): The currency manager.
        """
        self.handler = handler
        self.movement_manager = movement_manager
        self.items = items
        self.currency = currency
        self.bag = bag

    def _fetch_sell_offers(self) -> typing.Optional[list[dict]]:
        """
        Fetches the sell offers from the marketplace using the request handler.

        Returns:
            Optional[list[dict]]: The sell offers in the marketplace, if found. Otherwise, None.
        """
        result = self.handler.post(window="building_market", action="fetch_offers", payload={"page": "0"}, use_h=True)
        if result["error"] == True:
            raise Exception("Could not fetch offers")
        return result["msg"]["search_result"]

    def _fech_buy_offers(self) -> typing.Optional[list[dict]]:
        """
        Fetches the buy offers from the marketplace using the request handler.

        Returns:
            Optional[list[dict]]: The buy offers in the marketplace, if found. Otherwise, None.
        """
        result = self.handler.post(window="building_market", action="fetch_bids", payload={"page": "0"}, use_h=True)
        if result["error"] == True:
            raise Exception("Could not fetch offers")
        return result["msg"]["search_result"]

    def _assemble_offer_list(self, offers_data: list[dict]) -> Marketplace_offer_list:
        """
        Converts raw offer data into a Marketplace_offer_list.

        Args:
            offers_data (list[dict]): The raw offer data from the marketplace.

        Returns:
            Marketplace_offer_list: The list of offers.
        """
        return Marketplace_offer_list(
            offer_list=[Marketplace_offer(x) for x in offers_data],
            handler=self.handler,
            items=self.items
        )

    def search_sell_offers(self) -> Marketplace_offer_list:
        """
        Searches and returns the list of sell offers on the marketplace.

        Returns:
            Marketplace_offer_list: The list of sell offers.
        """
        return self._assemble_offer_list(offers_data=self._fetch_sell_offers())

    def search_buy_offers(self) -> Marketplace_offer_list:
        """
        Searches and returns the list of buy offers on the marketplace.

        Returns:
            Marketplace_offer_list: The list of buy offers.
        """
        return self._assemble_offer_list(offers_data=self._fech_buy_offers())

    def fetch_offer(self, offer: Marketplace_offer, is_buy: bool):
        """
        Fetches the given offer, moves to the offer's town, and updates bag or currency accordingly.

        Args:
            offer (Marketplace_offer): The offer to fetch.
            is_buy (bool): True if the offer is a buy offer, False for sell offers.
        """
        # Move to the town where the offer is located
        self.movement_manager.move_to_town(town=offer.town_id)

        # Fetch the offer using the handler
        result = offer.fetch_offer(handler=self.handler)

        # Check if fetching was successful
        if not result['succesfull']:
            raise Exception(f"Couldn't retrieve offer at the pickup manager level !")

        # Update bag or currency based on offer type
        if is_buy:
            self.bag.add_item(item_id=offer.item_id, amount=offer.item_count)
        else:
            self.currency.modify_cash(new_cash=result)

    def fetch_all_sold(self):
        """
        Fetches all sold offers from the marketplace. Sorts by distance to town and fetches accordingly.
        """
        # Get the list of sell offers and sort them by distance to town
        marketplace_offer_to_collect = self.search_sell_offers()
        marketplace_offer_to_collect.sort(key=lambda x: self.movement_manager.get_distance_to_town(x.town_id))

        # Iterate through sell offers and fetch them
        for offer in marketplace_offer_to_collect:
            if offer.sell_offer_completed_100_trust or offer.is_expired(self.handler):
                self.fetch_offer(offer=offer, is_buy=False)

    def fetch_all_bought(self):
        """
        Fetches all bought offers from the marketplace. Sorts by distance to town and fetches accordingly.
        """
        # Get the list of buy offers and sort them by distance to town
        marketplace_offer_to_collect = self.search_buy_offers()
        marketplace_offer_to_collect.sort(key=lambda x: self.movement_manager.get_distance_to_town(x.town_id))

        # Iterate through buy offers and fetch them
        for offer in marketplace_offer_to_collect:
            if offer.sell_offer_completed_100_trust or offer.is_expired(self.handler):
                self.fetch_offer(offer=offer, is_buy=True)
