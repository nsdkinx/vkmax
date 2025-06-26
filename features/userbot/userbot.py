import logging
from vkmax.client import MaxClient

_logger = logging.getLogger(__name__)

async def userbot(client: MaxClient, packet: dict):
    """ Userbot for vkmax """
    if packet['opcode'] == 128:
        cmd = packet['payload']['message']['text']
        if cmd == ".info":
            text = "Userbot connected"
            await client.invoke_method(67, {"chatId":packet["payload"]["chatId"],"messageId":packet["payload"]["message"]["id"],"text":text,"elements":[],"attachments":[]})



