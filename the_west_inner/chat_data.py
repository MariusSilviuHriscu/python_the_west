from dataclasses import dataclass
import typing

class ChatRoomData:
    
    def __init__(self , name : str , members : list[str] , is_private : bool):
        self.name = name
        self.members = members
        self.is_private = is_private
    
    def add_member(self , member : str):
        self.members.append(member)
    
    def add_members(self , members : typing.Iterable[str]):
        self.members.extend(members)
    
    def remove_member(self , member : str):
        self.members.remove(member)
    
    def remove_members(self , members : typing.Iterable[str]):
        for member in members:
            self.remove_member(member)
    
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
    
    @staticmethod
    def create_from_dict(data : dict):
        return ClientData(
            name = data['name'],
            cclass= data['cclass'],
            subclass= data['subclass'],
            westid= data['westid'],
            level= data['level'],
            duelLevel= data['duelLevel'],
            townId= data['townId'],
            town_rights= data['town_rights'],
            allianceId= data['allianceId'],
            gm= data['gm'],
            professionId= data['professionId'],
            id= data['id'],
            town_x= data['town_x'],
            town_y= data['town_y'],
            v= data['v'],
            actioned= data['actioned']
        )

class ClientDataManager:
    
    def __init__(self , clients : dict[str , ClientData]):
        self.clients = clients
    
    def add_client(self , client : ClientData):
        self.clients[client.id] = client
    
    def add_clients(self , clients : typing.Iterable[ClientData]):
        
        for client in clients:
            self.add_client(client)
    
    def set_clients(self , clients : typing.Iterable[ClientData]):
        self.clients = {client.id : client for client in clients}

    def remove_client(self , client_id : str):
        self.clients.pop(client_id)
    
    def __getitem__(self , client_id : str) -> ClientData:
        for client in self.clients.values():
            if client.name == client_id:
                return client
            if client.id == client_id:
                return client
    
    def player_exists(self , player_name : str) -> bool:
        for client in self.clients.values():
            if client.name == player_name:
                return True
        return False
@dataclass
class MessageData:
    message_content: str
    message_timestamp: int
    message_sender: str
    message_room: str
    
    def __hash__(self) -> int:
        return hash((self.message_content, self.message_timestamp, self.message_sender, self.message_room))



class ChatData:
    
    def __init__(self , messages : dict[MessageData] , rooms : list[ChatRoomData] , clients : ClientDataManager):
        self.messages = messages
        self.rooms = rooms
        self.clients = clients
    
    
    def add_message(self , message : MessageData):
        
        if message not in self.messages:
            self.messages[message] = message
    
    def add_messages(self , messages : list[MessageData]):
        for message in messages:
            self.add_message(message)
    
    
    def set_clients(self , clients : typing.Iterable[ClientData]):
        self.clients.set_clients(clients = clients)
    
    def add_clients_to_room(self ,clients : typing.Iterable[ClientData], room_name : str):
        print('adding clients to room: ', clients, room_name)
        is_private = 'room' not in room_name
        if room_name not in [x.name for x in self.rooms]:
            self.rooms.append(ChatRoomData(name = room_name , members = [] , is_private = is_private))
        for room in self.rooms:
            if room.name == room_name:
                room.add_members(clients = clients)
                return
    
    def remove_clients_from_room(self , clients : typing.Iterable[ClientData] , room_name : str):
        
        if room_name not in [x.name for x in self.rooms]:
            return
        for room in self.rooms:
            if room.name == room_name :
                room.remove_members(clients = clients)
                return
                
    def add_clients(self , clients : typing.Iterable[ClientData]| ClientData):
        if isinstance(clients , ClientData):
            self.clients.add_client(client = clients)
        else:
            self.clients.add_clients(clients = clients)
    def remove_client(self , client_id : str):
        self.clients.remove_client(client_id)
    
    def set_rooms(self , rooms : list[ChatRoomData]):
        self.rooms = rooms
    
    def get_general_chat_room(self) -> ChatRoomData:
        print(self.rooms)
        for room in self.rooms:
            print(room.__dict__)
            if room.is_private == False:
                return room
    
    def player_exists(self , player_name : str) -> bool:
        return self.clients.player_exists(player_name = player_name)
    def get_player(self , player_name : str) -> ClientData:
        return self.clients[player_name]