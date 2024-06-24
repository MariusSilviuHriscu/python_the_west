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
            
            yield ChatRoomData( name = room_dict['id'],
                                members = room_dict['members'],
                                is_private = not room_dict['roomdescription']['public']
                                )
    
    def load_clients(self , client_data : list[dict] , self_data : dict) -> Generator[ClientData, None, None]:
        
        for client_dict in client_data:
            
            yield ClientData.create_from_dict(data = client_dict)
        
        if self_data is not None:
            yield ClientData.create_from_dict(data = self_data)
            
            
    
    def load(self, status_dict : dict  ) -> StatusData:
        
        payload = status_dict['payload']
        
        clients = self.load_clients(client_data = payload['clients'] , self_data = payload['self'])
        rooms = self.load_rooms(room_data = payload['rooms'])
        
        return StatusData(rooms = list(rooms),
                          clients = clients)


class TellReceivedTextParser:
    
    def load_tell_received_text(self , tell_received_text_dict : dict) -> MessageData:
        
        if tell_received_text_dict['id'] != 'TellReceived':
            raise ValueError('Not a tell received message!')
        
        payload = tell_received_text_dict['payload']
        
        return MessageData(
            message_content = payload['message'],
            message_timestamp = tell_received_text_dict['t'],
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
            message_timestamp = text_dict['t'],
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
    client_data : ClientData | None = None
class JoinedClientParser:
    
    def load(self , joined_client_dict : dict) -> JoinedLeaveClientData:
        
        if joined_client_dict['id'] != 'ClientJoined' and joined_client_dict['id'] != 'ClientLeft':
            raise ValueError('Not a joined or left client message!')
        
        payload = joined_client_dict['payload']
        
        if joined_client_dict['id'] == 'ClientJoined':
            return JoinedLeaveClientData(
                id = payload['client']['id'],
                room_id = payload['rid'],
                time = joined_client_dict['t'],
                joined = True ,
                client_data = ClientData.create_from_dict(payload['client'])
            )
        elif joined_client_dict['id'] == 'ClientLeft':
            return JoinedLeaveClientData(
                id = payload['cid'],
                room_id = payload['rid'],
                time = joined_client_dict['t'],
                joined = False
            )

        else:
            raise ValueError('Unknown joined client message type!')
        
        

class ChatDataParser:
        
    def __init__(self ):
        self.status_data_parser = StatusDataParser()
        self.tell_received_text_parser = TellReceivedTextParser()
        self.joined_client_parser = JoinedClientParser()
    
    def add_batch(self, batch : dict) -> Generator[MessageData | StatusData | JoinedLeaveClientData, None, None]:
        
        event_function_map = {
            'Text' : self.tell_received_text_parser.load,
            'TellReceived' : self.tell_received_text_parser.load,
            'Status' : self.status_data_parser.load,
            'ClientJoined' : self.joined_client_parser.load,
            'ClientLeft' : self.joined_client_parser.load
        }
        
        for message in batch:
            if message['id'] not in event_function_map:
                continue
            yield event_function_map[message['id']](message)