import typing
from requests_handler import requests_handler
from movement_manager import MovementManager
from marketplace_buy import Marketplace_offer,Marketplace_offer_list
from items import Items
from currency import Currency
from bag import Bag

class MarketplacePickupManager:
    
    def __init__(self ,
                 handler: requests_handler ,
                 movement_manager :MovementManager,
                 items : Items,
                 bag : Bag,
                 currency : Currency
                 ):
        
        self.handler = handler
        self.movement_manager = movement_manager
        self.items = items
        self.currency = currency
        self.bag = bag
    def _fetch_sell_offers(self) -> typing.Optional[list[dict]]:
        """
        This function fetches the offers in the marketplace using the request handler.


        Returns:
        Optional[list[dict]]: The offers in the marketplace, if found. Otherwise, None.
        """
        result = self.handler.post(window="building_market",action="fetch_offers",payload={"page":"0"},use_h=True)
        if result["error"] == True:
            raise Exception("Could not fetch offers")
        return  result["msg"]["search_result"]
    def _fech_buy_offers(self) -> typing.Optional[list[dict]]:
        """
        This function fetches the offers in the marketplace using the request handler.


        Returns:
        Optional[list[dict]]: The offers in the marketplace, if found. Otherwise, None.
        """
        result = self.handler.post(window="building_market",action="fetch_bids",payload={"page":"0"},use_h=True)
        if result["error"] == True:
            raise Exception("Could not fetch offers")
        return  result["msg"]["search_result"]
    def _assemble_offer_list(self,offers_data : list[dict]) -> Marketplace_offer_list:
        """
        This function searches for the sell offers on the marketplace.

        Returns:
        Marketplace_offer_list: The list of offers on the marketplace.
        """
        return Marketplace_offer_list(
            offer_list=[Marketplace_offer(x) for x in offers_data],
            handler=self.handler,
            items=self.items
        )
    def search_sell_offers(self) -> Marketplace_offer_list:
        return self._assemble_offer_list(offers_data = self._fetch_sell_offers())
    def search_buy_offers(self) -> Marketplace_offer_list:
        return self._assemble_offer_list(offers_data= self._fech_buy_offers())
    def fetch_offer(self , offer : Marketplace_offer , is_buy:bool):
        self.movement_manager.move_to_town(town = offer.town_id)
        result = offer.fetch_offer(handler=self.handler)
        if not result['succesfull']:
            raise Exception(f"Couldn't retrive offer at the pickup manager level !")
        if is_buy :
            self.bag.add_item(item_id = offer.item_id,amount = offer.item_count)
        else:
            self.currency.modify_cash(new_cash=result)
    def fetch_all_sold(self):
        marketplace_offer_to_collect = self.search_sell_offers()
        for offer in marketplace_offer_to_collect:
            self.movement_manager.move_to_town(offer.town_id)
            if offer.sell_offer_completed_100_trust or offer.is_expired(self.handler):
                self.fetch_offer(offer = offer , is_buy=False)
    def fetch_all_bought(self):
        marketplace_offer_to_collect = self.search_buy_offers()
        for offer in marketplace_offer_to_collect:
            self.movement_manager.move_to_town(offer.town_id)
            if offer.sell_offer_completed_100_trust or offer.is_expired(self.handler):
                self.fetch_offer(offer = offer , is_buy=True)
