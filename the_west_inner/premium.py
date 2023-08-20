"""
This class handles the premium features that a player has access to in a game. It stores the active premium features as attributes and provides a method for extracting the active premium features from a dictionary of premium data.
"""

import time
import datetime
import typing

class Premium:
    """
    A class representing the premium features that a player has access to in a game.
    """
    
    def __init__(self, premium_data: typing.Dict[str, typing.Any], current_time: datetime.datetime):
        """
        Initializes the class with the player's premium data and the current time.
        
        Args:
            premium_data: A dictionary containing the player's premium data, including expiration dates for each premium feature.
            current_time: The current time, used to determine which premium features are active.
        """
        # Extract the active premium features from the premium data dictionary.
        premium_features = self.extract_active_premium_features(premium_data, current_time)
        
        # Store the active premium features as class attributes.
        self.automation = premium_features["automation"]
        self.character = premium_features["character"]
        self.money = premium_features["money"]
        self.regen = premium_features["regen"]
        self.greenhorn = premium_features["greenhorn"]
        self.vip = premium_features["vip"]
        
        # If the player has the VIP premium feature, they also have access to all other premium features.
        if self.vip:
            self.automation = True
            self.character = True
            self.money = True
            self.regen = True
            self.greenhorn = True
    
    def extract_active_premium_features(self, premium_data, current_time: datetime.datetime) -> typing.Dict[str, bool]:
        """
        Extracts the active premium features from the premium data dictionary.
        
        Args:
            premium_data: A dictionary containing the player's premium data, including expiration dates for each premium feature.
            current_time: The current time, used to determine which premium features are active.
        
        Returns:
            A dictionary containing the active premium features, with the feature names as keys and a boolean value indicating
            whether the feature is active or not.
        """
        # Initialize an empty dictionary to store the active premium features.
        active_features = {}
        
        # Loop through each premium feature in the premium data dictionary.
        for feature_name, feature_data in premium_data.items():
            # Parse the expiration date for the current premium feature.
            expiration_date = time.ctime(float(feature_data["expiration"]))
            expiration_date = datetime.datetime.strptime(expiration_date, "%c")
            
            # Check if the premium feature is active (i.e. its expiration date is after the current time).
            # If it is, add it to the active_features dictionary.
            if expiration_date > current_time:
                active_features[feature_name] = True
            else:
                active_features[feature_name] = False
        
        # Return the dictionary of active premium features.
        return active_features

