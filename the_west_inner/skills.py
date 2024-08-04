import typing
import json
from dataclasses import dataclass
from enum import Enum, auto

from the_west_inner.requests_handler import requests_handler

class CharacterSkillsEnum(Enum):
    # Attributes
    STRENGTH = auto()
    MOBILITY = auto()
    DEXTERITY = auto()
    CHARISMA = auto()

    # Strength-based skills
    BUILD = auto()
    PUNCH = auto()
    TOUGH = auto()
    ENDURANCE = auto()
    HEALTH = auto()

    # Mobility-based skills
    RIDE = auto()
    REFLEX = auto()
    DODGE = auto()
    HIDE = auto()
    SWIM = auto()

    # Dexterity-based skills
    AIM = auto()
    SHOT = auto()
    PITFALL = auto()
    FINGER_DEXTERITY = auto()
    REPAIR = auto()

    # Charisma-based skills
    LEADERSHIP = auto()
    TACTIC = auto()
    TRADE = auto()
    ANIMAL = auto()
    APPEARANCE = auto()

    def __str__(self):
        return self.name.lower()
    @classmethod
    def get_all_skills(cls):
        attributes = {'STRENGTH', 'MOBILITY', 'DEXTERITY', 'CHARISMA'}
        return [skill.name.lower() for skill in cls if skill.name not in attributes]
    @classmethod
    def get_all_attributes(cls):
        attributes = {'STRENGTH', 'MOBILITY', 'DEXTERITY', 'CHARISMA'}
        return [attribute.name.lower() for attribute in cls if attribute.name in attributes]
    @staticmethod
    def map_str_dict_to_enum_dict(str_dict) -> typing.Dict[typing.Self, int]:
        enum_dict = {}
        for key, value in str_dict.items():
            try:
                enum_key = CharacterSkillsEnum[key.upper()]
                enum_dict[enum_key] = value
            except KeyError:
                raise ValueError(f"{key} is not a valid CharacterSkillsEnum member")
        
        return enum_dict
class Skill_change_verifier():
    """
    The Skill_change_verifier class verifies if it is possible to make a given set of changes to skills and attributes.
    Also is used as a way to separate attribute and skill changes.
    Attributes:

        attribute_to_skill_mapping_dict (dict): a dictionary that maps attributes to a list of skills
        change_dict (dict): a dictionary that maps a skill or attribute name to the number of changes desired
    Methods:

        create_skills_dict: creates a dictionary that maps a skill to the number of changes desired
        create_attribute_dict: creates a dictionary that maps an attribute to the number of changes desired
        skill_points_used: calculates the total number of skill points used
        has_enough_free_skill_points: checks if there are enough free skill points to make the desired changes
        attribute_points_used: calculates the total number of attribute points used
        has_enough_free_attribute_points: checks if there are enough free attribute points to make the desired changes
        _return_skill_attribute_points_exceptions: returns an exception depending on whether there are enough skill and attribute points
        verify_changes: verifies if the desired changes can be made
        return_valid_skill_change_payload: returns a dictionary with the change payload
    """
    # a dictionary that maps attributes to a list of skills
    attribute_to_skill_mapping_dict = {
    'strength': ['build', 'punch', 'tough', 'endurance', 'health'],
    'flexibility': ['ride', 'reflex', 'dodge', 'hide', 'swim'],
    'dexterity': ['aim', 'shot', 'pitfall', 'finger_dexterity', 'repair'],
    'charisma': ['leadership', 'tactic', 'trade', 'animal', 'appearance']
    }
    def __init__(self, change_dict: typing.Dict[str, int]):
        # initialize the change dictionary
        self.change_dict = change_dict

    def create_skills_dict(self) -> typing.Dict[str, int]:
        """
        Creates a dictionary that maps a skill to the number of changes desired.
        
        Returns:
            A dictionary that maps a skill to the number of changes desired.
        """
        skill_dict = dict()
        # iterate over the change dictionary
        for skill_attribute_key, number_of_changes in self.change_dict.items():
            # if the key is not a skill, skip it
            if skill_attribute_key not in [skill_name for attribute_skills in self.attribute_to_skill_mapping_dict.values() for skill_name in attribute_skills]:
                continue
            # add the skill and number of changes to the skill dictionary
            skill_dict[skill_attribute_key] = number_of_changes
        return skill_dict

    def create_attribute_dict(self) -> typing.Dict[str, int]:
        """
        Creates a dictionary that maps an attribute to the number of changes desired.
        
        Returns:
            A dictionary that maps an attribute to the number of changes desired.
        """
        attribute_dict = dict()
        # iterate over the change dictionary
        for skill_attribute_key, number_of_changes in self.change_dict.items():
            # if the key is not an attribute, skip it
            if skill_attribute_key not in self.attribute_to_skill_mapping_dict.keys():
                continue
            # add the attribute and number of changes to the attribute dictionary
            attribute_dict[skill_attribute_key] = number_of_changes
        return attribute_dict

    def skill_points_used(self):
        """
        Calculates the total number of skill points used.
        
        Returns:
            An integer representing the total number of skill points used.
        """
        return sum(self.create_skills_dict().values())

    def has_enough_free_skill_points(self, available_points: int) -> bool:
        """
        Checks if there are enough free skill points to make the desired changes.
        
        Args:
            available_points: an integer representing the number of available skill points.
            
        Returns:
            A boolean indicating whether there are enough free skill points to make the desired changes.
        """
        return self.skill_points_used() <= available_points

    def attribute_points_used(self):
        """
        Calculates the total number of attribute points used.
        
        Returns:
            An integer representing the total number of attribute points used.
        """
        return sum(self.create_attribute_dict().values())

    def has_enough_free_attribute_points(self, available_points: int) -> bool:
        """
        Checks if there are enough free attribute points to make the desired changes.
        
        Args:
            available_points: an integer representing the number of available attribute points.
            
        Returns:
            A boolean indicating whether there are enough free attribute points to make the desired changes.
        """
        return self.attribute_points_used() <= available_points

    def _return_skill_attribute_points_exceptions(self, enough_skill_points: bool, enough_attribute_points: bool):
        """
        Returns an exception depending on whether there are enough skill and attribute points.
        
        Args:
            enough_skill_points: a boolean indicating whether there are enough free skill points.
            enough_attribute_points: a boolean indicating whether there are enough free attribute points.
            
        Returns:
            An exception indicating the problem with the skill or attribute points.
        """
        # create a tuple of the skill and attribute points
        points_tuple = (enough_skill_points, enough_attribute_points)
        # initialize the exception
        exception = None
        # check the tuple and set the exception accordingly
        if points_tuple == (False, False):
            exception = Exception("You do not have enough skill points or attribute points to make these changes.")
        elif points_tuple == (True, False):
            exception = Exception("You do not have enough attribute points to make these changes.")
        elif points_tuple == (False, True):
            exception = Exception("You do not have enough skill points to make these changes.")
        return exception

    def verify_changes(self, free_skill_points: int, free_attribute_points: int):
        """
        Verifies if the desired changes can be made.
        
        Args:
            free_skill_points: an integer representing the number of available skill points.
            free_attribute_points: an integer representing the number of available attribute points.
            
        Raises:
            Exception: if there are duplicate keys in the change dictionary,
                    if the keys in the change dictionary are not valid attribute or skill names,
                    or if there are not enough skill or attribute points to make the desired changes.
        """
        # check for duplicate keys in the change dictionary
        if len(set(self.change_dict.keys())) != len(self.change_dict.keys()):
            raise Exception("Duplicate change dictionary keys !")
        
        # create lists of the skills and attributes to be changed
        skill_list = self.create_skills_dict()
        attribute_list = self.create_attribute_dict()
        # find any keys that are not valid attribute or skill names
        invalid_keys = [x for x in self.change_dict.keys() if (x not in skill_list and x not in attribute_list)]
        
        # if there are any invalid keys, raise an exception
        if len(invalid_keys) != 0:
            raise Exception(f"The keys {invalid_keys} are not valid attribute or skill names")
        
        # check if there are enough skill and attribute points
        enough_skill_points = self.has_enough_free_skill_points(available_points=free_skill_points)
        enough_attribute_points = self.has_enough_free_attribute_points(available_points=free_attribute_points)
        
        # get the exception for the skill and attribute points
        number_skill_attribute_exception = self._return_skill_attribute_points_exceptions(enough_skill_points=enough_skill_points,
                                                                                        enough_attribute_points=enough_attribute_points)
        
        # if there is an exception, raise it
        if number_skill_attribute_exception is not None:
            raise number_skill_attribute_exception
    def return_valid_skill_change_payload(self, modifier: str) -> dict:
        """
        Returns a dictionary with the change payload.
        
        Args:
            modifier: a string indicating the type of modification ("add" or "remove")
        
        Returns:
            A dictionary with the change payload.
        """
        # create the change payload dictionary
        payload = {
            "modifier": modifier,
            "data": json.dumps({
                "attribute_modifications": self.create_attribute_dict(),
                "skill_modifications": self.create_skills_dict(),
                "attribute_points_used": int(self.attribute_points_used()),
                "skill_points_used": int(self.skill_points_used())
            })
        }
        return payload



@dataclass
class Skills:
    """
    A data class representing the skills data.
    
    Fields:
    - reskill_buyable: bool
        A boolean indicating whether reskill options are buyable.
    - skills_buyable: bool
        A boolean indicating whether skill points are buyable.
    - buyskills_costs: int
        The cost of buying skill points.
    - buyattributes_costs: int
        The cost of buying attribute points.
    - attributes_buyable: bool
        A boolean indicating whether attribute points are buyable.
    - actual_reskill_options: Dict[str,int]
        A dictionary containing the cost of reskilling skills and attributes.
    - shaman_visible: bool
        A boolean indicating whether the shaman is visible.
    - used_attributes: int
        The number of used attribute points.
    - used_skills: int
        The number of used skill points.
    - open_attr_points: int
        The number of open attribute points.
    - open_skill_points: int
        The number of open skill points.
    - skills: Dict[str,int]
        A dictionary of skills and their levels.
    - skill_bonuspoints: Dict[str,int]
        A dictionary of skills and their bonus points.
    - attributes: Dict[str,int]
        A dictionary of attributes and their levels.
    - attribute_bonuspoints: Dict[str,int]
        A dictionary of attributes and their bonus points.
    """
    reskill_buyable: bool
    skills_buyable: bool
    buyskills_costs: int
    buyattributes_costs: int
    attributes_buyable: bool
    actual_reskill_options: typing.Dict[str,int]
    shaman_visible: bool
    used_attributes: int
    used_skills: int
    open_attr_points: int
    open_skill_points: int
    skills: typing.Dict[str,int]
    skill_bonuspoints: typing.Dict[str,int]
    attributes: typing.Dict[str,int]
    attribute_bonuspoints: typing.Dict[str,int]
    def get_skill_value(self, skill: str) -> int:
        """Returns the value of the given skill.
        
        Args:
            skill: The name of the skill.
            
        Returns:
            The value of the given skill.
        """
        return self.skills[skill] + self.skill_bonuspoints.get(skill,0)
    def get_attribute(self, attribute: str) -> int:
        """Returns the value of the given attribute.
        
        Args:
            attribute: The name of the attribute.
            
        Returns:
            The value of the given attribute.
        """
        return self.attributes.get(attribute,0) + self.attribute_bonuspoints.get(attribute,0)
    def save_additional_skills_attributes(self, handler: requests_handler, changes: typing.Dict[str, int]):
        """
        Saves additional skills and attributes.
        
        Args:
            handler: an instance of the `requests_handler` class for making requests
            changes: a dictionary that maps a skill or attribute name to the number of changes desired
        
        Returns:
            The response from the server.
            
        Raises:
            Exception: If the server returns an error.
        """
        # create a Skill_change_verifier object
        verifier = Skill_change_verifier(change_dict=changes)
        
        # verify if the changes can be made
        verifier.verify_changes(
            free_skill_points=self.open_skill_points,
            free_attribute_points=self.open_attr_points
        )
        
        # send a request to save the skill changes
        response = handler.post(
            window="skill",
            action="save_skill_changes",
            # use the return_valid_skill_change_payload method to get the change payload
            payload=verifier.return_valid_skill_change_payload(modifier="add"),
            use_h=True
        )
        
        # if the server returns an error, raise an exception
        if response['error']:
            raise Exception(response['msg'])
        
        # Update the instance using the response data
        try:
            self._update(data=response, attribute_to_skill_mapping_dict=verifier.attribute_to_skill_mapping_dict)
        except Exception as e:
            print(response)
            raise e
        # return the response
        return response
    def _update(self, data: dict, attribute_to_skill_mapping_dict: dict):
        """Updates the instance fields using the given data dictionary.
        
        Args:
            data: A dictionary containing the updated skills data.
            attribute_to_skill_mapping_dict: A dictionary mapping attributes to a list of skills.
        Returns:
            None
        """
        # Calculate the difference between the current attribute values and the updated values
        differential_attribute_dict = {
            attribute: updated_value - self.attributes[attribute]
            for attribute, updated_value in data['char']['attributes'].items()
        }
        # Calculate the difference between the current skill bonus points and the updated values
        differential_skill_dict = {
            skill: differential_attribute_dict[attribute]
            for attribute, skill_list in attribute_to_skill_mapping_dict.items()
            for skill in skill_list
        }

        # Update the skill bonus points
        self.skill_bonuspoints = {
            skill: value + differential_skill_dict[skill]
            for skill, value in self.skill_bonuspoints.items()
        }

        # Update the skills and attributes
        self.skills = data['char']['skills']
        self.attributes = data['char']['attributes']
        # Update the number of open skill and attribute points
        self.open_skill_points = data['char']['skill_points']
        self.open_attr_points = data['char']['attribute_points']
    def set_skills_and_attributes_bonus(self,change_dict:typing.Dict[str,int]) -> None:
        """ 
        Updates the bonus skill and bonus attribute as a change of equipment.
        
        Args:
            change_dict: A dictionary containing the bonus attributes and skills
        
        Returns:
            None
        """
        #Create a Skill_change_verifier object
        verifier = Skill_change_verifier(change_dict=change_dict)
        #Calculate and set the attribute component of the change_dict
        self.attribute_bonuspoints = verifier.create_attribute_dict()
        #Calculate and set the skill component of the change_dict
        self.skill_bonuspoints = verifier.create_skills_dict()
def read_skill(handler: requests_handler) -> Skills:
    """Reads the skill data and returns a Skills instance.

    Args:
        handler: An instance of the requests_handler class.

    Returns:
        A Skills instance containing the skill data.
    """
    # Make a request to get the skill data
    response = handler.post(
        window= "skill",
        action="overview",
        action_name="mode"
    )
    # Initialize the Skills instance with the data from the response
    skills = Skills(
        reskill_buyable = response.get('reskill_buyable',None),
        skills_buyable = response['skills_buyable'],
        buyskills_costs = response['buyskills_costs'],
        buyattributes_costs = response['buyattributes_costs'],
        attributes_buyable = response['attributes_buyable'],
        actual_reskill_options = response['actualReskillOptions'],
        shaman_visible = response['shamanVisible'],
        used_attributes = response['usedAttributes'],
        used_skills = response['usedSkills'],
        open_attr_points = response['open_attrPoints'],
        open_skill_points = response['open_skillPoints'],
        skills = response['skills'],
        skill_bonuspoints = response['skillBonuspoints'] if response['skillBonuspoints'] != [] else {},
        attributes = response['attributes'],
        attribute_bonuspoints = response['attributeBonuspoints'] if response['attributeBonuspoints'] else {}
    )
    return skills