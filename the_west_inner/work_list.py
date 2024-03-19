
from requests_handler import requests_handler
    
class Work_list():
    """A class for managing a list of work items.

    Attributes:
        work_dict (dict): A dictionary of work items, indexed by their ID.
    """

    def __init__(self, work_list):
        """Initialize the work list.

        Args:
            work_list (list): A list of work items.
        """
        self.work_dict = {work["id"]:work for work in work_list}

    def get_group_id(self, work_id):
        """Get the group ID of a work item.

        Args:
            work_id (int): The ID of the work item.

        Returns:
            int: The group ID of the work item.
        """
        return self.work_dict[work_id]["groupid"]

    def work_products(self):
        """Get a dictionary of possible products that can be produced by the work items.

        Returns:
            dict: A dictionary mapping each product to its associated work item ID and level.
        """
        possible_yields = {}
        for yields in self.work_dict.values():
            # Skip items that don't have yields.
            if type(yields) == list:
                continue
            for product in yields["yields"]:
                # Add the product to the dictionary if it hasn't been seen before.
                if product not in possible_yields:
                    possible_yields[product] = None

        for work in self.work_dict.values():
            # Skip items that don't have yields.
            if type(work["yields"]) == list:
                continue
            for product in work["yields"].keys():
                # Associate the product with its work item ID and level.
                possible_yields[product] = {"id": work["id"], "level": work["level"]}

        return possible_yields

    def motivation(self, handler: requests_handler):
        """Get the motivation levels of the work items.

        Args:
            handler (requests_handler): An object for handling HTTP requests.

        Returns:
            dict: A dictionary mapping each work item's ID to its motivation level.
        """
        # Send an HTTP request to get the motivation levels of the work items.
        motivation_dict = handler.post(window="work", action="index", action_name="mode")["jobs"]

        # Return a dictionary mapping each work item's ID to its motivation level.
        return {x: int(float(motivation_dict[x]['motivation']) * 100) for x in motivation_dict}
