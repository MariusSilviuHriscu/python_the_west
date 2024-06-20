from dataclasses import dataclass
from typing import Generator,Iterable

from the_west_inner.chat_data import ChatRoomData
from the_west_inner.chat_data import ClientData,MessageData


class StatusData:
    
    def __init__(self , rooms : list[ChatRoomData] , clients : Iterable[ClientData]):
        self.rooms = rooms
        self.clients = clients

class StatusDataParser:
    
    
    def load_rooms(self , room_data : list[dict]) -> Generator[ChatRoomData, None, None]:
        
        for room_dict in room_data:
            
            yield ChatRoomData(room_dict['id'],
                                room_dict['members'],
                                not room_dict['roomdescription']['public']
                                )
    
    def load_clients(self , client_data : list[dict]) -> Generator[ClientData, None, None]:
        
        for client_dict in client_data:
            
            yield ClientData.create_from_dict(client_dict)
            
            
    
    def load(self, status_dict : dict  ) -> StatusData:
        
        payload = status_dict['payload']
        
        clients = self.load_clients(payload['clients'])
        rooms = self.load_rooms(payload['rooms'])
        
        return StatusData(rooms = list(rooms),
                          clients = clients)


class TellReceivedTextParser:
    
    def load_tell_received_text(self , tell_received_text_dict : dict) -> MessageData:
        
        if tell_received_text_dict['id'] != 'TellReceived':
            raise ValueError('Not a tell received message!')
        
        payload = tell_received_text_dict['payload']
        
        return MessageData(
            message_content = payload['message'],
            message_timestamp = payload['t'],
            message_sender = payload['from']['id'],
            message_room = payload['from']['id']
        )
    
    def load_tell_confirmed_text(self , tell_confirmed_text_dict : dict) -> MessageData:
        
        if tell_confirmed_text_dict['id'] != 'TellConfirmed':
            raise ValueError('Not a tell confirmed message!')
        
        payload = tell_confirmed_text_dict['payload']
        
        return MessageData(
            message_content = payload['message'],
            message_timestamp = payload['t'],
            message_sender = payload['to']['id'],
            message_room = payload['to']['id']
        )
    def load_text(self , text_dict : dict) -> MessageData:
        
        if text_dict['id'] != 'Text':
            raise ValueError('Not a text message!')
        
        payload = text_dict['payload']
        
        return MessageData(
            message_content = payload['message'],
            message_timestamp = payload['t'],
            message_sender = payload['cid'],
            message_room = payload['to']
        )
    def load(self, tell_received_text_dict : dict) -> MessageData:
        
        match tell_received_text_dict['id']:
            case 'TellReceived':
                return self.load_tell_received_text(tell_received_text_dict)
            case 'TellConfirmed':
                return self.load_tell_confirmed_text(tell_received_text_dict)
            case 'Text':
                return self.load_text(tell_received_text_dict)
            case _:
                raise ValueError('Unknown tell received message type!')
@dataclass
class JoinedLeaveClientData:
    id : str
    room_id : str
    time : int
    joined : bool
class JoinedClientParser:
    
    def load(self , joined_client_dict : dict) -> JoinedLeaveClientData:
        
        if joined_client_dict['id'] != 'ClientJoined':
            raise ValueError('Not a joined client message!')
        
        payload = joined_client_dict['payload']
        
        if payload['id'] == 'ClientJoined':
            return JoinedLeaveClientData(
                id = payload['client']['id'],
                room_id = payload['rid'],
                time = payload['t'],
                joined = True
            )
        elif payload['id'] == 'ClientLeft':
            return JoinedLeaveClientData(
                id = payload['client']['id'],
                room_id = payload['rid'],
                time = payload['t'],
                joined = False
            )
        else:
            raise ValueError('Unknown joined client message type!')
        
        

class ChatDataParser:
        
    def __init__(self ):
        self.status_data_parser = StatusDataParser()
        self.tell_received_text_parser = TellReceivedTextParser()
        self.joined_client_parser = JoinedClientParser()
    
    def _get_general_chat_room_messages(self , message_list : list[dict]):
        return [x for x in message_list if x['id'] == 'Text']
    
    def _get_tell_received_messages(self , message_list : list[dict]):
        return [x for x in message_list if x['id'] == 'TellReceived' or x['id'] == 'TellConfirmed']
    
    def _get_status_data(self , message_list : list[dict]):
        return [x for x in message_list if x['id'] == 'Status']
    
    def _get_joined_client_data(self , message_list : list[dict]):
        return [x for x in message_list if x['id'] == 'ClientJoined']
    
    def _get_left_client_data(self , message_list : list[dict]):
        return [x for x in message_list if x['id'] == 'ClientLeft']
    
    def _get_text_data(self , message_list : list[dict]):
        return [x for x in message_list if x['id'] == 'Text']
    
    def parse_message(self, message_list):
        return [x for x in message_list if x['id'] == 'Text'] , [x for x in message_list if x['id'] == 'TellReceived']
    
    def add_batch(self, batch : dict) -> Generator[dict, None, None]:
        
        event_function_map = {
            'Text' : self.tell_received_text_parser.load,
            'TellReceived' : self.tell_received_text_parser.load,
            'Status' : self.status_data_parser.load,
            'ClientJoined' : self.joined_client_parser.load,
            'ClientLeft' : self.joined_client_parser.load
        }
        
        for message in batch:
            if message['id'] == 'Text':
                yield event_function_map[message['id']](message)