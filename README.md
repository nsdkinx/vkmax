# python-max-client
Python client library for VK MAX messenger (OneMe)

[![PyPI version](https://badge.fury.io/py/python-max-client.svg)](https://badge.fury.io/py/python-max-client)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What is VK MAX?
MAX (internal code name OneMe) is another project by the Russian government in an attempt to create a unified domestic messaging platform with features such as login via the government services account (Gosuslugi/ESIA).  
It is developed by VK Group.  

## What is `python-max-client`?
This is a comprehensive client library for VK MAX messenger, allowing you to create userbots, custom clients, and automated solutions.  
The library provides a simple and intuitive API for interacting with the MAX messenger protocol.

## Features
- 🔐 **Authentication**: Support for SMS and token-based login
- 💬 **Messaging**: Send, receive, and edit messages
- 👥 **Users & Groups**: Manage users, groups, and channels
- 🔄 **Real-time**: WebSocket-based real-time communication
- 🛠️ **Extensible**: Easy to extend with custom functionality
- 📱 **Userbot Support**: Create powerful userbots and automation

## Installation
The package is available on PyPI:
```bash
pip install python-max-client
```

Or install from source:
```bash
git clone https://github.com/huxuxuya/python-max-client.git
cd python-max-client
pip install -e .
```

## Usage
More in [examples](examples/)
```python
import asyncio
import logging

import requests
import sys

from python_max_client.client import MaxClient
from python_max_client.functions.messages import edit_message

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

## Documentation
- [Protocol description](docs/protocol.md)
- [Known opcodes](docs/opcodes.md)

## Examples
Check out the [examples](examples/) directory for more usage examples:
- [Weather Userbot](examples/weather-userbot/) - Simple userbot that provides weather information
- [Ayumax](examples/ayumax/) - Advanced userbot example

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author
**huxuxuya** - [huxuxuya@gmail.com](mailto:huxuxuya@gmail.com)

## Acknowledgments
- Original project by [nsdkinx](https://github.com/nsdkinx/vkmax)
- VK Group for developing the MAX messenger platform
