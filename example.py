import asyncio
import logging

import requests
import sys

from python_max_client.client import MaxClient
from python_max_client.functions.messages import edit_message

from pathlib import Path

date_format = '%d.%m.%Y %H:%M:%S'
logging_format = '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'

handlers = [
    logging.StreamHandler(sys.stdout)
]

logging.basicConfig(
    format=logging_format,
    datefmt=date_format,
    handlers=handlers,
    level=logging.INFO
)

async def get_weather(city: str) -> str:
    response = requests.get(f"https://ru.wttr.in/{city}?Q&T&format=3")
    return response.text


async def packet_callback(client: MaxClient, packet: dict):
    if packet['opcode'] == 128:
        message_text: str = packet['payload']['message']['text']
        if message_text not in ['.info', '.weather']:
            return

        if message_text == ".info":
            text = "Userbot connected"

        elif ".weather" in message_text:
            city = message_text.split()[1]
            text = await get_weather(city)

        await edit_message(
            client,
            packet["payload"]["chatId"],
            packet["payload"]["message"]["id"],
            text
        )


async def main():
    client = MaxClient()

    await client.connect()

    login_token_file = Path('login_token.txt')

    if login_token_file.exists():
        login_token_from_file = login_token_file.read_text(encoding='utf-8').strip()
        try:
            await client.login_by_token(login_token_from_file)
        except:
            print("Couldn't login by token. Falling back to SMS login")

    else:
        phone_number = input('Your phone number: ')
        sms_login_token = await client.send_code(phone_number)
        sms_code = int(input('Enter SMS code: '))
        account_data = await client.sign_in(sms_login_token, sms_code)

        login_token = account_data['payload']['tokenAttrs']['LOGIN']['token']
        login_token_file.write_text(login_token, encoding='utf-8')

    await client.set_callback(packet_callback)

    await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
