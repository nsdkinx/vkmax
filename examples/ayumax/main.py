import sqlite3
import logging

from python_max_client.client import MaxClient
from python_max_client.functions.messages import send_message

_logger = logging.getLogger(__name__)

async def sql(cmd: str):
    db = sqlite3.connect('vkmax//features//ayumax//messages.db'); cur = db.cursor(); cur.execute(cmd); db.commit()
    fetcher = cur.fetchall(); cur.close(); db.close()
    if "SELECT" in cmd:
        return fetcher
    
async def incoming_message(chat_id: int, message_id: int, text: str):
    await sql(f"INSERT INTO messages(message_id, chat_id, text) VALUES({message_id}, {chat_id}, '{text}')")

async def edited_message(message_id: int, edited_text: str):
    if await sql(f"SELECT * FROM messages WHERE message_id = {message_id}") != []:
        await sql(f"UPDATE messages SET edited_text = '{edited_text}', status = 'EDITED' WHERE message_id = {message_id}")
    else:
        await sql(f"INSERT INTO messages(message_id, edited_text, status) VALUES({message_id}, '{edited_text}', 'EDITED')")

async def deleted_message(message_id: int):
    if await sql(f"SELECT * FROM messages WHERE message_id = {message_id}") != []:
        await sql(f"UPDATE messages SET status = 'REMOVED' WHERE message_id = {message_id}")
    else:
        await sql(f"INSERT INTO messages(message_id, status) VALUES({message_id}, 'DELETED')")

async def get_edited_messages(chat_id: int):
    return await sql(f"SELECT * FROM messages WHERE chat_id = {chat_id} AND status = 'EDITED'")

async def get_deleted_messages(chat_id: int):
    return await sql(f"SELECT * FROM messages WHERE chat_id = {chat_id} AND status = 'REMOVED'")

async def ayumax_callback(client: MaxClient, packet: dict):
    """ аюграм подкрался незаметно... """
    if packet['opcode'] == 128:
        message_text = packet['payload']['message']['text']
        print(packet)
        if (
            'status' in packet['payload']['message']
            and packet['payload']['message']['status'] == "REMOVED"
        ):
            await deleted_message(packet['payload']['message']['id'])
            await send_message(client, packet["payload"]["chatId"], text=f"Собеседник удалил сообщение: {message_text}")

        elif (
            'status' in packet['payload']['message']
            and packet['payload']['message']['status'] == "EDITED"
        ):
            await edited_message(int(packet["payload"]["message"]["id"]), message_text)
            previous_message = await sql(f"SELECT text FROM messages WHERE message_id = {int(packet["payload"]["message"]["id"])}")
            await send_message(client, packet["payload"]["chatId"], text=f"Собеседник изменил сообщение: {previous_message[0][0]}")
        else:
            await incoming_message(packet["payload"]["chatId"], int(packet["payload"]["message"]["id"]), message_text)
