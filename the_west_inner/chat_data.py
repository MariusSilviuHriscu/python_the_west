from dataclasses import dataclass


class ChatRoomData:
    
    def __init__(self , name : str , members : list[str] , is_private : bool):
        self.name = name
        self.members = members
        self.is_private = is_private
    
    def add_member(self , member : str):
        self.members.append(member)
    
    def remove_member(self , member : str):
        self.members.remove(member)
    
    def has_member(self , member : str) -> bool:
        return member in self.members

@dataclass
class ClientData:
    name: str
    cclass: str
    subclass: str
    westid: int
    level: int
    duelLevel: int
    townId: int
    town_rights: int
    allianceId: int
    gm: bool
    professionId: int
    id: str
    town_x: str
    town_y: str
    v: int
    actioned: int


@dataclass
class MessageData:
    message_content: str
    message_timestamp: int
    message_sender: str
    message_room: str
    
    def __hash__(self) -> int:
        return hash((self.message_content, self.message_timestamp, self.message_sender, self.message_room))



class ChatData:
    
    def __init__(self , messages : dict[MessageData] , rooms : list[ChatRoomData] , clients : dict[str , ClientData]):
        self.messages = messages
        self.rooms = rooms
        self.clients = clients
    
    
    def add_message(self , message : MessageData):
        
        if message not in self.messages:
            self.messages[message] = message
    
    def add_messages(self , messages : list[MessageData]):
        for message in messages:
            self.add_message(message)

    
    def get_messages_by_room(self , room : str) -> list[MessageData]:
        return [message for message in self.messages.values() if message.message_room == room]
    
    def remove_client(self , client_id : str,room : str):
        for room_data in self.rooms:
            if room_data.name == room and room_data.has_member(client_id):
                room_data.remove_member(client_id)
                