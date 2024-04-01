import typing

from gold_finder import parse_map_for_quest_employers
from work_manager import Work_manager
from requests_handler import requests_handler
from crafting import Crafting_table, acquire_product
from items import Items
from game_classes import Game_classes
from marketplace_buy import Marketplace_categories, search_marketplace_category, search_marketplace_item
from marketplace import Marketplace_buy_manager


class Quest_requirement:
    """
    Base class for representing quest requirements.
    """
    def __init__(self, solved: bool):
        """
        Initialize the Quest_requirement object.

        Args:
            solved (bool): Indicates if the requirement is solved or not.
        """
        self.solved = solved

    def declare_solved(self):
        """
        Mark the requirement as solved.
        """
        self.solved = True


class Quest_requirement_travel(Quest_requirement):
    """
    Represents a quest requirement related to travel.
    """
    priority = 3

    def __init__(self, x: int, y: int, employer_key: str, quest_id: int, solved: bool):
        """
        Initialize the Quest_requirement_travel object.

        Args:
            x (int): The x-coordinate of the target location.
            y (int): The y-coordinate of the target location.
            employer_key (str): The key of the quest employer.
            quest_id (int): The ID of the quest.
            solved (bool): Indicates if the requirement is solved or not.
        """
        self.x = x
        self.y = y
        self.employer_key = employer_key
        self.quest_id = quest_id
        super().__init__(solved)


class Quest_requirement_item_to_hand_work_product_hourly(Quest_requirement):
    """
    Represents a quest requirement related to crafting a product hourly.
    """
    priority = 1

    def __init__(self, item_id: int, number: int, quest_id: int, solved: bool):
        """
        Initialize the Quest_requirement_item_to_hand_work_product_hourly object.

        Args:
            item_id (int): The ID of the item to craft.
            number (int): The number of items to craft.
            quest_id (int): The ID of the quest.
            solved (bool): Indicates if the requirement is solved or not.
        """
        self.item_id = item_id
        self.number = number
        self.quest_id = quest_id
        super().__init__(solved)


class Quest_requirement_item_to_hand_work_product_seconds(Quest_requirement):
    """
    Represents a quest requirement related to crafting a product within a certain time frame.
    """
    priority = 1

    def __init__(self, item_id: int, number: int, quest_id: int, solved: bool):
        """
        Initialize the Quest_requirement_item_to_hand_work_product_seconds object.

        Args:
            item_id (int): The ID of the item to craft.
            number (int): The number of items to craft.
            quest_id (int): The ID of the quest.
            solved (bool): Indicates if the requirement is solved or not.
        """
        self.item_id = item_id
        self.number = number
        self.quest_id = quest_id
        super().__init__(solved)


class Quest_requirement_item_to_hand_buy_from_marketplace(Quest_requirement):
    """
    Represents a quest requirement related to buying items from the marketplace.
    """
    priority = 1

    def __init__(self, item_id: int, number: int, quest_id: int, solved: bool):
        """
        Initialize the Quest_requirement_item_to_hand_buy_from_marketplace object.

        Args:
            item_id (int): The ID of the item to buy.
            number (int): The number of items to buy.
            quest_id (int): The ID of the quest.
            solved (bool): Indicates if the requirement is solved or not.
        """
        self.item_id = item_id
        self.number = number
        self.quest_id = quest_id
        super().__init__(solved)


class Quest_requirement_item_to_buy_from_city_building(Quest_requirement):
    """
    Represents a quest requirement related to buying items from a city building.
    """
    priority = 1

    def __init__(self, item_id: int, number: int, quest_id: int, solved: bool):
        """
        Initialize the Quest_requirement_item_to_buy_from_city_building object.

        Args:
            item_id (int): The ID of the item to buy.
            number (int): The number of items to buy.
            quest_id (int): The ID of the quest.
            solved (bool): Indicates if the requirement is solved or not.
        """
        self.item_id = item_id
        self.number = number
        self.quest_id = quest_id
        super().__init__(solved)


class Quest_requirement_use_travelling_merchant_item(Quest_requirement):
    """
    Represents a quest requirement related to using items from the traveling merchant.
    """
    priority = 1

    def __init__(self, item_id: int, number: int, quest_id: int, solved: bool):
        """
        Initialize the Quest_requirement_use_travelling_merchant_item object.

        Args:
            item_id (int): The ID of the item to use.
            number (int): The number of items to use.
            quest_id (int): The ID of the quest.
            solved (bool): Indicates if the requirement is solved or not.
        """
        self.item_id = item_id
        self.number = number
        self.quest_id = quest_id
        super().__init__(solved)


class Quest_requirement_item_to_get_from_other_quest(Quest_requirement):
    """
    Represents a quest requirement related to obtaining items from another quest.
    """
    priority = 2

    def __init__(self, item_id: int, item_id_reward_quest: int, quest_id: int, solved: bool):
        """
        Initialize the Quest_requirement_item_to_get_from_other_quest object.

        Args:
            item_id (int): The ID of the item to obtain.
            item_id_reward_quest (int): The ID of the quest that rewards the item.
            quest_id (int): The ID of the quest.
            solved (bool): Indicates if the requirement is solved or not.
        """
        self.item_id = item_id
        self.item_id_reward_quest = item_id_reward_quest
        self.quest_id = quest_id
        super().__init__(solved)


class Quest_requirement_work_n_seconds(Quest_requirement):
    """
    Represents a quest requirement related to working for a certain duration.
    """
    priority = 1

    def __init__(self, work_id: int, required_work_time: int, solved: bool):
        """
        Initialize the Quest_requirement_work_n_seconds object.

        Args:
            work_id (int): The ID of the work.
            required_work_time (int): The required duration of work in seconds.
            solved (bool): Indicates if the requirement is solved or not.
        """
        self.work_id = work_id
        self.required_work_time = required_work_time
        super().__init__(solved)


class Quest_requirement_work_n_times(Quest_requirement):
    """
    Represents a quest requirement related to working for a certain number of times.
    """
    priority = 1

    def __init__(self, work_id: int, required_work_times: int, solved: bool):
        """
        Initialize the Quest_requirement_work_n_times object.

        Args:
            work_id (int): The ID of the work.
            required_work_times (int): The required number of times to work.
            solved (bool): Indicates if the requirement is solved or not.
        """
        self.work_id = work_id
        self.required_work_times = required_work_times
        super().__init__(solved)


class Quest_requirement_sell_item(Quest_requirement):
    """
    Represents a quest requirement related to selling an item.
    """
    priority = 2

    def __init__(self, item_id: int, solved: bool):
        """
        Initialize the Quest_requirement_sell_item object.

        Args:
            item_id (int): The ID of the item to sell.
            solved (bool): Indicates if the requirement is solved or not.
        """
        self.item_id = item_id
        super().__init__(solved)


class Quest_requirement_accept_other_quest(Quest_requirement):
    """
    Represents a quest requirement related to accepting another quest.
    """
    priority = 1

    def __init__(self, other_quest_id: int, solved: bool):
        """
        Initialize the Quest_requirement_accept_other_quest object.

        Args:
            other_quest_id (int): The ID of the other quest to accept.
            solved (bool): Indicates if the requirement is solved or not.
        """
        self.other_quest_id = other_quest_id
        super().__init__(solved)


class Quest_requirement_solve_other_quest(Quest_requirement):
    """
    Represents a quest requirement related to solving another quest.
    """
    priority = 1

    def __init__(self, other_quest_id: int, solved: bool):
        """
        Initialize the Quest_requirement_solve_other_quest object.

        Args:
            other_quest_id (int): The ID of the other quest to solve.
            solved (bool): Indicates if the requirement is solved or not.
        """
        self.other_quest_id = other_quest_id
        super().__init__(solved)


class Quest_requirement_distribute_skill_point(Quest_requirement):
    """
    Represents a quest requirement related to distributing skill points.
    """
    priority = 1

    def __init__(self, number_of_skill_points: int, solved: bool):
        """
        Initialize the Quest_requirement_distribute_skill_point object.

        Args:
            number_of_skill_points (int): The number of skill points to distribute.
            solved (bool): Indicates if the requirement is solved or not.
        """
        self.number_of_skill_points = number_of_skill_points
        super().__init__(solved)


class Quest_requirement_get_n_skill_points(Quest_requirement):
    """
    Represents a quest requirement related to obtaining a certain number of skill points.
    """
    priority = 1

    def __init__(self, target_number: int, skill_key: str, solved: bool):
        """
        Initialize the Quest_requirement_get_n_skill_points object.

        Args:
            target_number (int): The target number of skill points to obtain.
            skill_key (str): The key of the skill.
            solved (bool): Indicates if the requirement is solved or not.
        """
        self.target_number = target_number
        self.skill_key = skill_key
        super().__init__(solved)


class Quest_requirement_get_n_attribute_points(Quest_requirement):
    """
    Represents a quest requirement related to obtaining a certain number of attribute points.
    """
    priority = 1

    def __init__(self, target_number: int, attribute_key: str, solved: bool):
        """
        Initialize the Quest_requirement_get_n_attribute_points object.

        Args:
            target_number (int): The target number of attribute points to obtain.
            attribute_key (str): The key of the attribute.
            solved (bool): Indicates if the requirement is solved or not.
        """
        self.target_number = target_number
        self.attribute_key = attribute_key
        super().__init__(solved)


class Quest_requirement_duel_npc(Quest_requirement):
    """
    Represents a quest requirement related to dueling an NPC.
    """
    priority = 1

    def __init__(self, quest_id: int, solved: bool):
        """
        Initialize the Quest_requirement_duel_npc object.

        Args:
            quest_id (int): The ID of the quest.
            solved (bool): Indicates if the requirement is solved or not.
        """
        self.quest_id = quest_id
        super().__init__(solved)


class Quest_requirement_duel_quest_npc(Quest_requirement):
    """
    Represents a quest requirement related to dueling a quest NPC.
    """
    priority = 3

    def __init__(self, quest_id: int, solved: bool = True):
        """
        Initialize the Quest_requirement_duel_quest_npc object.

        Args:
            quest_id (int): The ID of the quest.
            solved (bool, optional): Indicates if the requirement is solved or not. Defaults to True.
        """
        self.quest_id = quest_id
        super().__init__(solved)


class Quest_requirement_equip_item(Quest_requirement):
    """
    Represents a quest requirement related to equipping an item.
    """
    priority = 1

    def __init__(self, item_id: int, solved: bool = True):
        """
        Initialize the Quest_requirement_equip_item object.

        Args:
            item_id (int): The ID of the item to equip.
            solved (bool, optional): Indicates if the requirement is solved or not. Defaults to True.
        """
        self.item_id = item_id
        super().__init__(solved)


class Quest_requirement_work_quest_item(Quest_requirement):
    """
    Represents a quest requirement related to working with a quest item.
    """
    priority = 1

    def __init__(self, item_id: int, work_id: int, solved: bool):
        """
        Initialize the Quest_requirement_work_quest_item object.

        Args:
            item_id (int): The ID of the quest item.
            work_id (int): The ID of the work.
            solved (bool): Indicates if the requirement is solved or not.
        """
        self.item_id = item_id
        self.work_id = work_id
        super().__init__(solved)


class Quest_requirement_list:
    """
    Represents a list of quest requirements.
    """
    def __init__(self, requirement_list: list[Quest_requirement]):
        """
        Initialize the Quest_requirement_list object.

        Args:
            requirement_list (list): List of quest requirements.
        """
        self.requirement_list = requirement_list

    @property
    def solved_requirements(self):
        """
        Check if all requirements in the list are solved.

        Returns:
            bool: True if all requirements are solved, False otherwise.
        """
        return all([x.solved for x in self.requirement_list])


def build_solved_quest_requirement(requirement_dict_iterables: typing.Iterable):
    """
    Build a list of solved quest requirements based on the given dictionary iterable.

    Args:
        requirement_dict_iterables (Iterable): Iterable containing dictionaries representing quest requirements.

    Returns:
        Quest_requirement_list: A list of solved quest requirements.
    """
    requirements = []
    for requirement_dict in requirement_dict_iterables:
        requirements.append(Quest_requirement(solved=requirement_dict['solved']))
    return Quest_requirement_list(requirement_list=requirements)
