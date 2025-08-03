# vkmax
Python user client for VK MAX messenger (OneMe)

## What is VK MAX?
MAX (internal code name OneMe) is another project by the Russian government in an attempt to create a unified domestic messaging platform with features such as login via the government services account (Gosuslugi/ESIA).  
It is developed by VK Group.  

## What is `vkmax`?
This is a client library for MAX, allowing to create userbots and custom clients.  
An example of a simple userbot that retrieves weather can be found at [examples/weather-userbot](examples/weather-userbot).

## Installation
The package is [available on PyPI](https://pypi.org/project/vkmax/)  
`pip install vkmax`

## Usage
More in [examples](examples/)
```python
import asyncio
import logging

import requests
import sys

from vkmax.client import MaxClient
from vkmax.functions.messages import edit_message

from pathlib import Path


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
        phone_number = input('Enter your phone number: ')
        sms_login_token = await client.send_code(phone_number)
        sms_code = int(input('Enter SMS code: '))
        account_data = await client.sign_in(sms_login_token, sms_code)

        login_token = account_data['payload']['tokenAttrs']['LOGIN']['token']
        login_token_file.write_text(login_token, encoding='utf-8')

    await client.set_callback(packet_callback)

    await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
```

- [Protocol description](docs/protocol.md)
- [Known opcodes](docs/opcodes.md)
