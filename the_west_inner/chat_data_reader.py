from typing import Generator


class MessagesParser:
    def __init__(self):
        self.messages = {}
    
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