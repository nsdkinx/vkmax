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
from pathlib import Path

import aiohttp

from vkmax.client import MaxClient
from vkmax.functions.messages import edit_message


# global aiohttp session
http = None


async def get_weather(city: str) -> str:
    global http
    if not http:
        http = aiohttp.ClientSession()
    response = await http.get(f"https://ru.wttr.in/{city}?Q&T&format=3")
    return await response.text()


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

    session_file = Path('max_session.txt')

    if not session_file.exists():
        phone_number = input('Enter your phone number: ')
        sms_token = await client.send_code(phone_number)
        sms_code = int(input('Enter SMS code: '))
        account_data = await client.sign_in(sms_token, sms_code)

        device_id = client.device_id
        login_token = account_data['payload']['tokenAttrs']['LOGIN']['token']

        # save device uuid and auth token delimited by newline
        session_file.write_text(f'{device_id}\n{login_token}')

    else:
        contents = session_file.read_text()
        device_id, login_token = contents.split('\n', maxsplit=1)
        try:
            await client.login_by_token(login_token, device_id)
        except:
            print("Couldn't login by token")

    await client.set_callback(packet_callback)

    await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
```

- [Protocol description](docs/protocol.md)
- [Known opcodes](docs/opcodes.md)
