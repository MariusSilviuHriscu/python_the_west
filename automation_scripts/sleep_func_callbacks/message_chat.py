import typing

from the_west_inner.chat_data_reader import StatusData, JoinedLeaveClientData , MessageData
from the_west_inner.chat import Chat
from the_west_inner.chat import ChatHandler
from the_west_inner.chat_data import ChatData, ClientDataManager
from the_west_inner.chat_data_reader import ChatDataParser

from automation_scripts.sleep_func_callbacks.check_marketplace_for_item import Flag
from the_west_inner.requests_handler import requests_handler

ChatGeneratorType = typing.Generator[MessageData|StatusData|JoinedLeaveClientData, None, None]




def send_message_to_chat(message : str , chat_generator : ChatGeneratorType , chat : Chat , flag : Flag | None = None):
    
    if flag :
        return
    
    
    sent = False
    for chat_entity in chat_generator:
    
        if not sent and chat.chat_data.get_general_chat_room() is not None:
            print(f'sending to {chat.chat_data.get_general_chat_room().name}')
            pending_message = chat.send_message(
            recipient_name=chat.chat_data.get_general_chat_room().name,
            message= f'{message}'
            )
            chat.message_queue.append(pending_message)
            
            sent = True

        if sent and isinstance(chat_entity , MessageData):
            if chat_entity.message_content == message:
                return

def message_chat(message : str ,handler : requests_handler, flag : Flag | None = None):
    def clean_message(message : str):
        if message.endswith(' '):
            return clean_message(message = message.removesuffix(' '))
        return message
        
    chat_handler = ChatHandler(
    handler = handler
    )

    client_data_manager = ClientDataManager(clients={})

    chat_data = ChatData({},[],clients=client_data_manager)

    chat_data_parser = ChatDataParser()
    
    chat = Chat(
    chat_handler = chat_handler,
    chat_data = chat_data,
    chat_data_parser=chat_data_parser
    )
    chat_generator = chat.message_loop()
    
    send_message_to_chat(
        message= clean_message(message=message),
        chat_generator = chat_generator,
        chat = chat,
        flag = flag
    )