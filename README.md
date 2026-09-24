# python-max-client

> **Fork Notice**: This is a fork of the original [vkmax](https://github.com/nsdkinx/vkmax) project by [nsdkinx](https://github.com/nsdkinx). This fork is maintained for personal development and improvements.

Python user client for VK MAX messenger (OneMe)

## What is VK MAX?
MAX (internal code name OneMe) is another project by the Russian government in an attempt to create a unified domestic messaging platform with features such as login via the government services account (Gosuslugi/ESIA).  
It is developed by VK Group.  

## What is `vkmax`?
This is a client library for MAX, allowing to create userbots and custom clients.  
An example of a simple userbot that retrieves weather can be found at [examples/weather-userbot](examples/weather-userbot).

## Features
- 🔐 Authentication via SMS or saved token (with custom `device_id`)
- 💬 Send, reply, edit messages with attachments
- 📎 Photo / video / file uploads (`vkmax.functions.uploads`)
- 📋 Chats snapshot cached at login (`get_cached_chats`, see [SAVE_CHATS_README](SAVE_CHATS_README.md))
- 🤖 Telegram bridge bot (see [implementation notes](TELEGRAM_BOT_IMPLEMENTATION_COMPLETE.md))
- 🔄 Realtime WebSocket with keepalive and reconnect callback

## Installation
This fork is not published to PyPI under the `vkmax` name — install from source:
```bash
git clone -b save_chats https://github.com/huxuxuya/python-max-client.git
cd python-max-client
pip install -r requirements.txt
```
> For the original stable package use `pip install vkmax` ([nsdkinx/vkmax](https://github.com/nsdkinx/vkmax)).

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

    client.set_packet_callback(packet_callback)

    await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
```

## API Reference

### MaxClient (`vkmax.client`)
- `connect()` / `disconnect()` - Connect/disconnect (stops keepalive and receiver)
- `send_code(phone)` - Send SMS code, returns login token
- `sign_in(token, code)` - Sign in with SMS code
- `login_by_token(token, device_id=None)` - Login with saved token
- `device_id` (property) - Device id of the current session
- `get_cached_chats()` - Chats cached from the login response (if any)
- `set_packet_callback(cb)` - Async incoming-packet handler
- `set_reconnect_callback(cb)` - Async handler fired on disconnect
- `set_callback(cb)` - Deprecated async alias of `set_packet_callback`

### Functions
- `vkmax.functions.messages` - `send_message` (with `reply_to`/`attaches`), `edit_message`, `reply_message`, `send_photo`, `send_file`
- `vkmax.functions.uploads` - `upload_photo`, `upload_video`, `upload_file`, `download_video`, `download_file`
- `vkmax.functions.chats` - Chat management, incl. cached-chats helpers
- `vkmax.functions.users` / `groups` / `channels` / `profile` - Entity management

## Documentation

## Original Project

This is a fork of the original [vkmax](https://github.com/nsdkinx/vkmax) project created by [nsdkinx](https://github.com/nsdkinx). 

**Original project links:**
- GitHub: https://github.com/nsdkinx/vkmax
- PyPI: https://pypi.org/project/vkmax/
- Telegram: https://t.me/max_messenger_python

## Fork Information

**python-max-client** is maintained for personal development and improvements. If you're looking for the original, stable version, please use the original project.
