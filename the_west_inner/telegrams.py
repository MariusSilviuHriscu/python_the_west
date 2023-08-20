from dataclasses import dataclass
import typing
from requests_handler import requests_handler

@dataclass
class Telegram_message_post():
    post_id: int
    player_id : int
    player_name : str
    text : str
    post_date : str
    is_male : bool
    title_id : int = None
    title_name : typing.Optional[str] = None
@dataclass
class Telegram_message():
    head_id : int
    ownbyme : bool
    pages : int
    title : str
    post_dict : typing.Dict[int,typing.List[Telegram_message_post]]
    def __add__(self,other:typing.Dict[int,typing.List[Telegram_message_post]]):
        if isinstance(other,dict):
            post_dict = self.post_dict
            for page,telegram_post_list in other.items():
                if page not in post_dict:
                    post_dict[page] = telegram_post_list
                else:
                    post_dict[page] += telegram_post_list
        elif isinstance(other,Telegram_message):
            post_dict = self.post_dict
            combine_dicts = lambda dict1, dict2: {
                    key: dict1[key] + [val for val in dict2[key] if val not in dict1[key]]
                        for key in dict1}
            post_dict = combine_dicts(post_dict,other.post_dict)
        elif isinstance(other,list):
            post_dict = self.post_dict
            add_to_dict = lambda d, value: d.update({max(d.keys())+1: value})
            post_dict = add_to_dict(post_dict,other)
        else:
            raise TypeError("Telegram_message only accepts dicts with lists of the Telegram_message_post value! or another Telegram_message object or a list of Telegram_message_post objects") 
        return Telegram_message(
            head_id = self.head_id,
            ownbyme = self.ownbyme,
            pages= self.pages,
            title= self.title, 
            post_dict= post_dict
            )
@dataclass
class Telegram():
    """A class representing a telegram message in a messaging system.

    Attributes:
        message_id: An integer representing the unique identifier of the telegram message.
        head_id: An integer representing the unique identifier of the telegram message thread.
        created_by: An integer representing the unique identifier of the user who created the telegram message.
        subject: A string representing the subject of the telegram message.
        partener_id: A list of integers representing the unique identifiers of the users who are part of the telegram message thread.
        partener_name: A list of strings representing the names of the users who are part of the telegram message thread.
        folder: A string representing the folder in which the telegram message is stored (default is empty string).

    Methods:
        read_message: Retrieves the telegram message from the messaging system.
        _read_message_by_page: Retrieves a specific page of the telegram message from the messaging system.
        _create_telegram_message: Creates an instance of the Telegram_message class based on the information provided in the response parameter.
        _create_telegram_message_post_list: Creates a list of instances of the Telegram_message_post class based on the information provided in the response parameter.
    """
    message_id:int
    head_id:int
    created_by:int
    subject:str
    partener_id:typing.List[int]
    partener_name:typing.List[str]
    folder:str=""
    def read_message(self, handler: requests_handler, read_all_posts: bool = False) -> Telegram_message:
        """Retrieves the telegram message from the messaging system.

        Args:
            handler: An instance of the requests_handler class that is used to make the request to the messaging system.
            read_all_posts: A boolean value indicating whether all posts in the telegram message should be read (default is False).

        Returns:
            An instance of the Telegram_message class that contains information about the telegram message.
        """

        # Retrieve the first page of the telegram message
        response_first_page = self._read_message_by_page(handler, 1)

        # Create an instance of the Telegram_message class from the first page of the telegram message
        telegram_message = self._create_telegram_message(response_first_page)

        # Add the posts from the first page of the telegram message to the Telegram_message instance
        telegram_message += {1:self._create_telegram_message_post_list(response_first_page)}

        # If read_all_posts is True, retrieve and add the remaining pages of the telegram message to the Telegram_message instance
        if read_all_posts:
            for page in range(2, response_first_page['pages']):
                telegram_message += {page:self._create_telegram_message_post_list(self._read_message_by_page(handler=handler, page=page))}

        # Return the Telegram_message instance
        return telegram_message
    def _read_message_by_page(self, handler: requests_handler, page: int) -> Telegram_message:
        """Retrieves a specific page of the telegram message from the messaging system.

        Args:
            handler: An instance of the requests_handler class that is used to make the request to the messaging system.
            page: An integer representing the page of the telegram message to be retrieved.

        Returns:
            A dictionary containing information about the telegram message for the specified page.
        """

        # Make a request to the messaging system using the provided handler to retrieve the specified page of the telegram message
        response = handler.post(
            window="messages",
            action="get_message",
            payload={"tid": f"{self.message_id}", "page": f"{page}"},
            use_h=True,
        )
        print(response)
        # If the request was not successful, raise an exception
        if "error" in response and response["error"] == True:
            raise Exception("Invalid minimap response")

        # Return the response from the messaging system
        return response
    def _create_telegram_message(self, response: dict) -> Telegram_message:
        """Creates an instance of the Telegram_message class based on the information provided in the response parameter.

        Args:
            response: A dictionary containing information about the telegram message.

        Returns:
            An instance of the Telegram_message class based on the information provided in the response parameter.
        """

        # Create an instance of the Telegram_message class with the information provided in the response parameter
        return Telegram_message(
            head_id=response["head_id"],
            ownbyme=response["ownbyme"],
            pages=response["pages"],
            title=response["subject"],
            post_dict={},
        )

    def _create_telegram_message_post_list(self, response: dict) -> Telegram_message_post:
        """Creates a list of instances of the Telegram_message_post class based on the information provided in the response parameter.

        Args:
            response: A dictionary containing information about the telegram message.

        Returns:
            A list of instances of the Telegram_message_post class based on the information provided in the response parameter.
        """

        # Create a list of instances of the Telegram_message_post class with the information provided in the response parameter
        return [
            Telegram_message_post(
                post_id = post["post_id"] ,
                player_id = post["player_id"] ,
                player_name = post["name"] ,
                text = post["text"] ,
                post_date = post["post_date"] ,
                is_male = post["is_male"] ,
                title_id = post["title_id"] ,
                title_name = post["title_name"] if "title_name" in post else "" ,
                )
            for post in response["posts"]
        ]

class Telegram_list:
    """A class representing a list of telegrams.

    Attributes:
        telegram_list: A list of instances of the Telegram class.

    Methods:
        __init__: Initializes the Telegram_list instance.
        __len__: Overrides the built-in len function to return the length of the telegram_list.
        __add__: Overrides the built-in + operator to add items to the telegram_list.
        __getitem__: Overrides the built-in [] operator to get items from the telegram_list.
        __iter__: Returns an iterator for the telegram_list.
        __next__: Returns the next item in the telegram_list.
    """

    def __init__(self, telegram_list: typing.List[Telegram] = []):
        """Initializes the Telegram_list instance.

        Args:
            telegram_list: A list of instances of the Telegram class (default is empty list).
        """

        self.telegram_list = telegram_list

    def __len__(self):
        """Overrides the built-in len function to return the length of the telegram_list.
        Returns:
            An integer representing the length of the telegram_list.
        """

        return len(self.telegram_list)

    def __add__(self, other: typing.Union["Telegram_list", typing.List[Telegram], Telegram]) -> "Telegram_list":
        """Overrides the built-in + operator to add items to the telegram_list.

        Args:
            other: An instance of the Telegram_list, a list of instances of the Telegram class, or an instance of the Telegram class.

        Returns:
            An instance of the Telegram_list with the added items.

        Raises:
            TypeError: If the other parameter is not an instance of the Telegram_list, a list of instances of the Telegram class, or an instance of the Telegram class.
        """

        # Check the type of the other parameter and add the appropriate items to the telegram_list
        if isinstance(other, Telegram_list):
            return Telegram_list(self.telegram_list + other.telegram_list)
        elif isinstance(other, list) and (
            all([isinstance(x, Telegram) for x in other]) or len(other) == 0
        ):
            return Telegram_list(self.telegram_list + other)
        elif isinstance(other, Telegram):
            return Telegram_list(self.telegram_list + [other])
        else:
            raise TypeError(f"Cannot add object of type '{type(other)}' to Telegram_list")

    def __getitem__(self, index: typing.Union[int, slice]):
        """Overrides the built-in [] operator to get items from the telegram_list.

        Args:
            index: An integer or slice representing the index or indices of the items to be retrieved.

        Returns:
            A list of instances of the Telegram class if the index is a slice.

        Raises:
            TypeError: If the index parameter is not an integer or slice.
        """

        # Check the type of the index parameter and retrieve the appropriate items from the telegram_list
        if isinstance(index, int):
            return self.telegram_list[index]
        elif isinstance(index, slice):
            start = index.start
            stop = index.stop
            step = index.step
            if start is None:
                start = 0
            if stop is None:
                stop = len(self.telegram_list)
            if step is None:
                step = 1

            return Telegram_list(self.telegram_list[start:stop:step])
        else:
            raise TypeError(f"Invalid type '{type(index)}' for indexing Telegram_list")

    def __iter__(self):
        """Returns an iterator for the telegram_list.

        Returns:
            An iterator for the telegram_list.
        """

        return iter(self.telegram_list)

    def __next__(self):
        """Returns the next item in the telegram_list.

        Returns:
            The next item in the telegram_list.
        """

        return self.telegram_list.__next__()

    
class Telegram_data_reader():
    """A class for reading telegram data.

    Attributes:
        handler: An instance of the requests_handler class.

    Methods:
        __init__: Initializes the Telegram_data_reader instance.
        get_data_by_page: Gets telegram data for a given page number.
        get_data: Gets all telegram data (optionally reading all pages).
    """
    def __init__(self, handler: requests_handler) -> None:
        """Initializes the Telegram_data_reader instance.

        Args:
            handler: An instance of the requests_handler class.
        """

        self.handler = handler

    def get_data_by_page(self, page_number: int) -> typing.Dict[str, typing.Union[int, Telegram_list]]:
        """Gets telegram data for a given page number.

        Args:
            page_number: An integer representing the page number to get telegram data for.

        Returns:
            A dictionary containing the total number of pages and a list of telegram data for the given page number.

        Raises:
            Exception: If there is an error getting the telegram data for the given page number.
        """

        # Make a post request to get the telegram data for the given page number
        response = self.handler.post(
            window="messages",
            action="get_messages",
            payload={
                "folder_id": "all",
                "page": f"{page_number}",
                "include_blocked": "1",
            },
            use_h=True,
        )

        # Raise an exception if there is an error getting the telegram data for the given page number
        if response["error"]:
            raise Exception(
                f"Getting the telegram data for the page number {page_number} did not work!"
            )

        # Create a list of Telegram instances using the telegram data from the response
        telegram_list = []
        for message in response["messages"]:
            telegram = Telegram(
                message_id=message["message_id"],
                head_id=message["head_id"],
                created_by=message["createby"],
                subject=message["subject"],
                partener_id=message["partner_id"],
                partener_name=message["partner_name"],
            )
            telegram_list.append(telegram)
        # Return the total number of pages and the list of Telegram instances
        return {"num_max_pages": response["count"], "telegram_list": Telegram_list(telegram_list)}

    def get_data(self, read_all_pages: bool = False):
        """Gets all telegram data (optionally reading all pages).

        Args:
            read_all_pages: A boolean indicating whether to read all pages of telegram data (defaults to False).

        Returns:
            A list of telegram data.
        """

        # Get the telegram data for the first page
        first_page_response = self.get_data_by_page(page_number=1)

        # Initialize the telegram_list with the telegram data from the first page
        telegram_list = first_page_response["telegram_list"]

        # If read_all_pages is True, get the telegram data for all pages and append it to the telegram_list
        if read_all_pages:
            for i in range(2, first_page_response["num_max_pages"] + 1):
                page_response = self.get_data_by_page(page_number=i)
                telegram_list += page_response["telegram_list"]

        # Return the telegram_list
        return telegram_list