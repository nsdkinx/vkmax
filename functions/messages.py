import logging
from random import randint

from vkmax.client import MaxClient

_logger = logging.getLogger(__name__)

async def send_message(client: MaxClient, chat_id: int, text: str, notify=True):
    """ Sends message to chat """
    await client.invoke_method(64, {
    "chatId": chat_id,
    "message": {
      "text": text,
      "cid": randint(1750000000000, 2000000000000),
      "elements": [],
      "attaches": []
    },
    "notify": notify
    }
  )
    
async def edit_message(client: MaxClient, chat_id: int, message_id: int, text: str):
    """ Edits message in specified chat """
    await client.invoke_method(67, {
    "chatId":chat_id,
    "messageId":str(message_id),
    "text":text,
    "elements":[],
    "attachments":[]
      }
    )
