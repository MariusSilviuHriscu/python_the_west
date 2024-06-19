from typing import Generator




class ChatDataParser:
        
    
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
    
    def parse_message(self, message_list):
        return [x for x in message_list if x['id'] == 'Text'] , [x for x in message_list if x['id'] == 'TellReceived']
    
    def add_batch(self, batch) -> Generator[dict, None, None]:
        
        saloon_messages , tell_messages = self.parse_message(batch)
        
        for message in saloon_messages:
            if (message['t'] , message['payload']['cid'], message['payload']['message']) not in self.messages:
                
                self.messages[(message['t'] , message['payload']['cid'], message['payload']['message'])] = message
                yield message
        for message in tell_messages:
            if (message['t'] , message['payload']['from']['id'], message['payload']['message']) not in self.messages:
                self.messages[(message['t'] , message['payload']['from']['id'], message['payload']['message'])] = message
                yield message