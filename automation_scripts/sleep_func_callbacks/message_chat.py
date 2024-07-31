import typing

from the_west_inner.chat_data_reader import StatusData, JoinedLeaveClientData , MessageData
from the_west_inner.chat import Chat

from automation_scripts.sleep_func_callbacks.check_marketplace_for_item import Flag

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