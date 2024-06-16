import time
import string
import random
import json
from dataclasses import dataclass
from urllib.parse import urlparse
from requests import Response
import typing

from requests_handler import requests_handler

@dataclass
class ChatRequestData:
    messageid : int
    clid : str
    stamp : int
    actioned : int
    batch : list
    def to_json(self):
        return json.dumps(self.__dict__)

class ChatSendRequest:
    def __init__(self, 
                 handler : requests_handler,
                 chat_request_data : ChatRequestData,
                 is_sent : bool = False   
                 ):
        self.handler = handler
        self.chat_request_data = chat_request_data
        self.is_sent = is_sent

    def send(self) -> Response:
        data = self.chat_request_data.to_json()
        return self.handler.session.post(
                    urlparse(self.handler.base_url)._replace(path="gameservice/chat/").geturl(), allow_redirects=False,
                    data= data
            )

class Chat:
    
    def __init__(self, handler : requests_handler):
        
        self.handler = handler
        self.clid = self.generate_client_connection_id()
    
    def generate_client_connection_id(self):
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
    
    def create_chat_request_data(self,message_id : int,clid : int, actioned  = None , recipient = 'null', message = None) -> ChatRequestData:
        # Get the current timestamp in milliseconds
        current_timestamp = int(time.time() * 1000)
        
        # Example values
        messageid = message_id  # Increment this value as needed
        last_actioned_time = actioned
        if actioned is None:
            last_actioned_time = current_timestamp - 129  # Example: a short time ago, adjust as needed
            
        batch = [{"op": "send", "to": recipient, "stamp": current_timestamp - 1 , "message" : message}] if message is not None else [
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
    
    def message_loop(self) -> typing.Generator[ChatSendRequest, None, None]:
        
        data  = self.create_chat_request_data(
            message_id = 1,
            clid=self.clid
            )
        
        chat_request = ChatSendRequest(
            handler = self.handler,
            chat_request_data = data 
            )
        
        yield chat_request
        
        
        actioned = int(time.time() * 1000) - 129
        i = 2
        while True:
            
            data = self.create_chat_request_data(
                message_id = i,
                clid=self.clid,
                actioned = actioned
                )
            
            chat_request = ChatSendRequest(
                handler = self.handler,
                chat_request_data = data 
                )
            
            yield chat_request
            i += 1