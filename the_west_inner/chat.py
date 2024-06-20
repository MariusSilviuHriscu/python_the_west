import time
import string
import random
import json
from dataclasses import dataclass
from urllib.parse import urlparse
from requests import Response
import typing

from requests_handler import requests_handler

from chat_data_reader import ChatDataParser, StatusData, JoinedLeaveClientData
from chat_data import ChatData, MessageData

@dataclass
class ChatRequestData:
    """
    Data class for holding chat request details.
    Attributes:
        messageid (int): Unique identifier for the message.
        clid (str): Client ID.
        stamp (int): Timestamp of the request.
        actioned (int): Timestamp of the last action.
        batch (list): List of actions (messages or operations).
    """
    messageid: int
    clid: str
    stamp: int
    actioned: int
    batch: list

    def to_json(self):
        """
        Serializes the data to a JSON string.
        Returns:
            str: JSON string representation of the chat request data.
        """
        return json.dumps(self.__dict__)

class ChatSendRequest:
    """
    Handles sending chat requests.
    Attributes:
        handler (requests_handler): Handler for making HTTP requests.
        chat_request_data (ChatRequestData): Chat request data object.
        is_sent (bool): Flag indicating if the request has been sent.
    """
    def __init__(self, 
                 handler: requests_handler,
                 chat_request_data: ChatRequestData,
                 is_sent: bool = False):
        self.handler = handler
        self.chat_request_data = chat_request_data
        self.is_sent = is_sent

    def send(self) -> Response:
        """
        Sends the chat request using the handler.
        Returns:
            Response: Response object from the HTTP request.
        """
        data = self.chat_request_data.to_json()
        return self.handler.session.post(
                    urlparse(self.handler.base_url)._replace(path="gameservice/chat/").geturl(), allow_redirects=False,
                    data=data
            )

class ChatHandler:
    """
    Manages chat sessions and requests.
    Attributes:
        handler (requests_handler): Handler for making HTTP requests.
        clid (str): Client ID.
        _index (int): Index for tracking message IDs.
    """
    def __init__(self, handler: requests_handler):
        self.handler = handler
        self.clid = self.generate_client_connection_id()
        self._index = 1
    
    @property
    def index(self) -> int:
        """
        Returns the current index and increments it.
        Returns:
            int: Current index value.
        """
        current_index = self._index
        self._index += 1
        return current_index

    def generate_client_connection_id(self) -> str:
        """
        Generates a unique client connection ID.
        Returns:
            str: Generated client connection ID.
        """
        # Get the current timestamp in milliseconds
        init_time = int(time.time() * 1000)
        
        # Create the base string with the alphabet and the timestamp
        base_string = string.ascii_lowercase + str(init_time)
        
        # Shuffle the base string
        base_list = list(base_string)
        random.shuffle(base_list)
        shuffled_string = ''.join(base_list)
        
        # Extract the substring from the shuffled string
        part1 = shuffled_string[5:23]
        
        # Extract the last 4 characters of the timestamp
        part2 = str(init_time)[-4:]
        
        # Concatenate the parts to form the client connection ID
        client_connection_id = part1 + part2
        
        return client_connection_id
    
    def create_chat_request_data(self, message_id: int, clid: int, actioned=None, recipient='null', message=None) -> ChatRequestData:
        """
        Creates a ChatRequestData object based on provided parameters.
        Args:
            message_id (int): Unique identifier for the message.
            clid (int): Client ID.
            actioned (int, optional): Timestamp of the last action. Defaults to None.
            recipient (str, optional): Recipient of the message. Defaults to 'null'.
            message (str, optional): Message content. Defaults to None.
        Returns:
            ChatRequestData: Created ChatRequestData object.
        """
        # Get the current timestamp in milliseconds
        current_timestamp = int(time.time() * 1000)
        
        # Example values
        messageid = message_id
        last_actioned_time = actioned
        if actioned is None:
            last_actioned_time = current_timestamp - 129
        
        batch = [{"op": "send", "to": recipient, "stamp": current_timestamp - 1, "message": message}] if message is not None else [
            {"op": "nop", "to": recipient, "stamp": current_timestamp - 1}
        ]
        
        # Create the data dictionary
        data = {
            "messageid": messageid,
            "clid": clid,
            "stamp": current_timestamp,
            "actioned": last_actioned_time,
            "batch": batch
        }
        
        return ChatRequestData(**data)
    
    def send(self, recipient: str, message: str) -> ChatSendRequest:
        """
        Sends a chat message.
        Args:
            recipient (str): Recipient of the message.
            message (str): Message content.
        Returns:
            ChatSendRequest: ChatSendRequest object ready to be sent.
        """
        actioned = int(time.time() * 1000) - 129
        data = self.create_chat_request_data(message_id=self.index, 
                                             clid=self.clid,
                                             actioned=actioned,
                                             recipient=recipient,
                                             message=message)
        return ChatSendRequest(handler=self.handler, chat_request_data=data)
    
    def message_loop(self) -> typing.Generator[ChatSendRequest, None, None]:
        """
        Generates chat requests in a loop.
        Yields:
            ChatSendRequest: ChatSendRequest object.
        """
        data = self.create_chat_request_data(
            message_id=self.index,
            clid=self.clid
        )
        
        chat_request = ChatSendRequest(
            handler=self.handler,
            chat_request_data=data
        )
        
        yield chat_request
        
        actioned = int(time.time() * 1000) - 129
        
        while True:
            data = self.create_chat_request_data(
                message_id=self.index,
                clid=self.clid,
                actioned=actioned
            )
            
            chat_request = ChatSendRequest(
                handler=self.handler,
                chat_request_data=data
            )
            
            yield chat_request

class Chat:
    """
    Coordinates chat handling and data processing.
    Attributes:
        chat_handler (ChatHandler): Handler for chat requests.
        chat_data (ChatData): Data storage for chat information.
        chat_data_parser (ChatDataParser): Parser for chat data.
        message_queue (list[ChatSendRequest]): Queue of messages to be sent.
    """
    def __init__(self, 
                 chat_handler: ChatHandler,
                 chat_data: ChatData,
                 chat_data_parser: ChatDataParser):
        self.chat_handler = chat_handler
        self.chat_data = chat_data
        self.chat_data_parser = chat_data_parser
        self.message_queue: list[ChatSendRequest] = []

    def send_message(self, recipient_name: str, message: str) -> typing.Union[ChatSendRequest, bool]:
        """
        Sends a message to a recipient if the recipient exists.
        Args:
            recipient_name (str): Name of the recipient.
            message (str): Message content.
        Returns:
            typing.Union[ChatSendRequest, bool]: ChatSendRequest object if recipient exists, otherwise False.
        """
        if not self.chat_data.player_exists(player_name=recipient_name):
            return False
        player_data = self.chat_data.get_player_data(player_name=recipient_name)
        
        return self.chat_handler.send(recipient=player_data.id, message=message)
    
    def parse_batch(self, batch: list[dict]) -> typing.Generator[typing.Union[MessageData, StatusData, JoinedLeaveClientData], None, None]:
        """
        Parses a batch of messages and updates chat data.
        Args:
            batch (list[dict]): Batch of messages to be parsed.
        Yields:
            typing.Union[MessageData, StatusData, JoinedLeaveClientData]: Parsed message data.
        """
        for message in self.chat_data_parser.add_batch(batch):
            if isinstance(message, MessageData):
                self.chat_data.add_message(message)
            elif isinstance(message, StatusData):
                self.chat_data.set_rooms(rooms=message.rooms)
                self.chat_data.set_clients(clients=message.clients)
            elif isinstance(message, JoinedLeaveClientData):
                if message.joined:
                    self.chat_data.add_clients(clients=message.client_data)
                else:
                    self.chat_data.remove_client(client_id=message.id)
            
            yield message
    
    def handle_request(self, chat_request: ChatSendRequest) -> typing.Generator[typing.Union[MessageData, StatusData, JoinedLeaveClientData], None, None]:
        """
        Handles a chat request and processes the response.
        Args:
            chat_request (ChatSendRequest): Chat request to be handled.
        Yields:
            typing.Union[MessageData, StatusData, JoinedLeaveClientData]: Parsed message data.
        """
        chat_request_response = chat_request.send()
        
        chat_request_data = json.loads(chat_request_response.text)
        batch = chat_request_data['batch']
        
        yield from self.parse_batch(batch=batch)
    
    def message_loop(self) -> typing.Generator[MessageData|StatusData|JoinedLeaveClientData, None, None]:
        """
        Processes messages in a loop, handling queued requests and sending new requests.
        Yields:
            ChatSendRequest: ChatSendRequest object.
        """
        for chat_request in self.chat_handler.message_loop():
            while len(self.message_queue) != 0:
                queue_chat_request = self.message_queue.pop(0)
                yield from self.handle_request(chat_request=queue_chat_request)
            
            yield from self.handle_request(chat_request=chat_request)
