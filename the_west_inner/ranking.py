from dataclasses import dataclass
from typing import Protocol
from enum import StrEnum

from the_west_inner.player_data import ClassTypeEnum
from the_west_inner.requests_handler import requests_handler



class CategoryEnum(StrEnum):
    EXPERIENCE = 'experience'

class SkillCategoryEnum(StrEnum):
    
    STRENGTH = 'strength'
    DEXTERITY = 'dexterity'
    CHARISMA = 'charisma'
    MOBILITY = 'mobility'

@dataclass
class PlayerRatingQuantity:
    player_place: int
    player_quantity: int


class PlayerInfo:
    def __init__(
        self,
        player_name: str,
        player_id: int,
        level: int,
        player_town_name: str = None,
        player_town_id: int = None,
    ):
        self.player_name = player_name
        self.player_id = player_id
        self.level = level
        self.player_town_name = player_town_name
        self.player_town_id = player_town_id

    def __hash__(self) -> int:
        return hash(self.player_id)

    def __eq__(self, other):
        if isinstance(other, PlayerInfo):
            return self.player_id == other.player_id
        return False

    def __repr__(self):
        return f"<PlayerInfo {self.player_name} (ID: {self.player_id})>"


class PlayerCategoryRating:
    def __init__(
        self, 
        rating_category: str, 
        player_rating_data: dict[PlayerInfo, PlayerRatingQuantity] = None
    ):
        self.rating_category = rating_category
        self.player_rating_data = player_rating_data if player_rating_data is not None else {}

    def add_player_rating(self, player_info: PlayerInfo, player_rating_quantity: PlayerRatingQuantity):
        if player_info in self.player_rating_data:
            return
        self.player_rating_data[player_info] = player_rating_quantity

    def get_player_rating(self, player_info: PlayerInfo | int) -> int | None:
        if isinstance(player_info, int):
            player_info = PlayerInfo("", player_info, 0)
        return self.player_rating_data.get(player_info, None).player_place if player_info in self.player_rating_data else None

    def get_player_quantity(self, player_info: PlayerInfo | int) -> int | None:
        if isinstance(player_info, int):
            player_info = PlayerInfo("", player_info, 0)
        return self.player_rating_data.get(player_info, None).player_quantity if player_info in self.player_rating_data else None

class PlayerRatingData:
    def __init__(
        self,
        player_pages: int = None,
        category_ratings: list[PlayerCategoryRating] = None,
        registered_players: set[PlayerInfo] = None
    ):
        self.category_ratings = category_ratings if category_ratings is not None else []
        self.player_pages = player_pages
        self.registered_players = registered_players if registered_players is not None else set()


    @property
    def pages_initialised(self) -> bool:
        return self.player_pages is not None

    def set_player_pages(self, player_pages: int):
        if player_pages < 1:
            raise ValueError("Number of player pages must be at least 1.")
        self.player_pages = player_pages

    @property
    def player_number_aprox(self) -> int:
        return (self.player_pages - 1) * 9

    def add_player(self, player_info: PlayerInfo):
        if player_info in self.player_registry:
            return
        self.player_registry.add(player_info)

    def player_in_rating(self, player_rating: PlayerInfo | int) -> bool:
        """
        Checks if a player is in the rating registry.
        Supports either PlayerInfo or player_id (int).
        Performs constant-time lookup due to hash-based implementation.
        """
        if isinstance(player_rating, PlayerInfo):
            return player_rating in self.player_registry
        elif isinstance(player_rating, int):
            dummy_player = PlayerInfo(player_name="", player_id=player_rating, level=0)
            return dummy_player in self.player_registry
        return False

class PlayerRatingHandler:
    def __init__(self, requests_handler: requests_handler):
        self.requests_handler = requests_handler

    def get_page_normal(self, category: str, page: int = 0) -> dict:
        response = self.requests_handler.post(
            window='ranking',
            action='get_data',
            action_name='mode',
            payload={
                'page': page,
                'tab': category
            }
        )
        if response.get('error'):
            raise ValueError("Failed to retrieve page numbers from the response.")
        return response
    
    def get_page_skill(self, skill : str , entries_per_page: int = 10) -> dict:
        response = self.requests_handler.post(
            window='ranking',
            action='get_data',
            action_name='skill',
            payload={
                'page': 0,
                'tab': 'skills',
                'skill': skill,
                'entries_per_page': entries_per_page
            }
        )
        if response.get('error'):
            raise ValueError("Failed to retrieve page numbers from the response.")
        return response


class PlayerRatingManager():
    
    def __init__(self , handler : requests_handler):
        
        self.handler = handler
        self.rating_handler = PlayerRatingHandler(requests_handler = handler)
        self.player_rating_data = PlayerRatingData()
    
    
    def _load_player_pages(self):
        result = self.rating_handler.get_page_normal(category=CategoryEnum.EXPERIENCE)
            
        pages = result.get('pages', 0)
        if pages < 1:
            raise ValueError("No pages found for the specified category.")
        
        self.player_rating_data.set_player_pages(player_pages=pages)
        
    @property
    def player_pages(self) -> int:
        
        if not self.player_rating_data.pages_initialised:
            
            self._load_player_pages()
        
        return self.player_rating_data.player_pages
    
    @property
    def aprox_player_number(self) -> int:
        if not self.player_rating_data.pages_initialised:
            self._load_player_pages()
        return self.player_rating_data.player_number_aprox
    
    def build_player_info(self, player_data: dict) -> PlayerInfo:
        
        return PlayerInfo(
            player_name= player_data.get('name'),
            player_id= player_data.get('player_id'),
            level= player_data.get('level'),
            player_town_name= player_data.get('town_name' , None),
            player_town_id= player_data.get('town_id', None)
        )
    def process_player_data(self, 
                            ranking_data : list[dict] , 
                            category_data : PlayerCategoryRating , 
                            category : str ) -> PlayerInfo:
        
        for player_data in ranking_data:
            
            player_info = self.build_player_info(player_data)
            player_position = player_data.get('counter')
            player_quantity_val = player_data.get(category)
            
            player_rating = PlayerRatingQuantity(
                player_place= player_position,
                player_quantity= player_quantity_val
            )
            
            category_data.add_player_rating(
                player_info= player_info,
                player_rating_quantity= player_rating
            )
    def get_player_experience_rating(self) -> PlayerCategoryRating:
            
        category_data = PlayerCategoryRating(rating_category= CategoryEnum.EXPERIENCE)
        
        for page in range(self.player_pages):
            result = self.get_page_normal(category= CategoryEnum.EXPERIENCE , page=page)
            self.process_player_data(
                ranking_data= result.get('ranking'),
                category_data= category_data,
                category= CategoryEnum.EXPERIENCE
            )
        
        
        return category_data
    
    def get_skill_rating(self, skill : SkillCategoryEnum) -> PlayerCategoryRating:
        
        skill_category_data = PlayerCategoryRating(rating_category= skill)
        
        result = self.rating_handler.get_page_skill(skill= skill,
                                                    entries_per_page= self.aprox_player_number
                                                    )
        
        self.process_player_data(
            ranking_data= result.get('ranking'),
            category_data= skill_category_data,
            category= 'skill_level'
        )
        
        return skill_category_data