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
- 🔐 **Authentication**: Support for SMS and token-based login (with custom `device_id`)
- 💬 **Messaging**: Send, reply, edit messages with attachments
- 📎 **Uploads**: Photos, videos and files (`python_max_client.functions.uploads`)
- 👥 **Users & Groups**: Manage users, groups, and channels
- 🔄 **Real-time**: WebSocket-based real-time communication with keepalive and reconnect callback
- 📋 **Chats snapshot**: Chats cached at login (`get_cached_chats`, see [SAVE_CHATS_README](SAVE_CHATS_README.md))
- 🤖 **Telegram bridge bot** (see [implementation notes](TELEGRAM_BOT_IMPLEMENTATION_COMPLETE.md))
- 🛠️ **Extensible**: Easy to extend with custom functionality
- 📱 **Userbot Support**: Create powerful userbots and automation

## Installation

### Quick Install
The package is available on PyPI and can be installed with pip:
```bash
pip install python-max-client
```

### Install from Source
If you want to install the latest development version:
```bash
git clone https://github.com/huxuxuya/python-max-client.git
cd python-max-client
pip install -e .
```

### Telegram bridge extras
The bot in [telegram_bot/](telegram_bot/) needs extra dependencies:
```bash
pip install -r telegram_bot/requirements.txt
```
Copy `telegram_bot/env_example.txt` to your env file and fill in tokens (never commit real tokens).

### Requirements
- Python 3.9 or higher
- Internet connection for VK MAX messenger access

### Dependencies
The package automatically installs the following dependencies:
- `websockets>=12.0` - WebSocket client for real-time communication
- `httpx>=0.25.0` - HTTP client for API requests
- `aiohttp` - HTTP client for file uploads and connection pooling
- `requests>=2.32.0` - HTTP client for examples

### Verify Installation
After installation, verify that the package works correctly:
```python
import python_max_client
print(f"python-max-client version: {python_max_client.__version__}")
print(f"Author: {python_max_client.__author__}")
```

## Usage

### Basic Example
Here's a simple example of how to use the library:

```python
import asyncio
from python_max_client import MaxClient

async def main():
    # Create a client instance
    client = MaxClient()
    
    # Connect to VK MAX
    await client.connect()
    
    # Login with phone number
    phone = input("Enter your phone number: ")
    sms_token = await client.send_code(phone)
    code = input("Enter SMS code: ")
    await client.sign_in(sms_token, int(code))
    
    # Set up message handler
    async def message_handler(client, packet):
        if packet['opcode'] == 128:  # New message
            print(f"New message: {packet['payload']['message']['text']}")
    
    await client.set_callback(message_handler)
    
    # Keep running
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
```

### Advanced Example
For more complex usage, check out the [examples](examples/) directory:

```python
import asyncio
from pathlib import Path

import aiohttp

from python_max_client import MaxClient
from python_max_client.functions.messages import edit_message


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

### MaxClient
The main client class for interacting with VK MAX messenger.

```python
from python_max_client import MaxClient

client = MaxClient()
```

#### Methods
- `connect()` - Connect to VK MAX servers
- `disconnect()` - Disconnect and stop background tasks
- `send_code(phone)` - Send SMS code to phone number
- `sign_in(token, code)` - Sign in with SMS code
- `login_by_token(token, device_id=None)` - Login with saved token and optional device id
- `device_id` (property) - Device id used for the current session
- `get_cached_chats()` - Chats cached from the login response (if any)
- `set_packet_callback(callback)` - Set async message handler callback
- `set_reconnect_callback(callback)` - Set async callback fired on disconnect (for custom reconnect logic)
- `set_callback(callback)` - Deprecated alias of `set_packet_callback`

### MaxPacket
Data class for handling VK MAX protocol packets.

```python
from python_max_client import MaxPacket

packet = MaxPacket(
    ver=1,
    cmd=0,
    opcode=128,
    seq=1,
    payload={"message": {"text": "Hello!"}}
)
```

### Functions
The library provides various functions for different operations:

- `python_max_client.functions.messages` - Message operations (send/reply/edit, `send_photo`, `send_file`)
- `python_max_client.functions.uploads` - File uploads/downloads (`upload_photo`, `upload_video`, `upload_file`, `download_video`, `download_file`)
- `python_max_client.functions.users` - User management
- `python_max_client.functions.groups` - Group operations
- `python_max_client.functions.chats` - Chat management
- `python_max_client.functions.channels` - Channel operations
- `python_max_client.functions.profile` - Profile management

> **Note:** a historical `vkmax/` package snapshot (from `save_chats` work) is also present
> in-tree. The canonical package is `python_max_client`; `tests/` cover both layouts.

## Documentation
- [Protocol description](docs/protocol.md)
- [Known opcodes](docs/opcodes.md)

## Examples
Check out the [examples](examples/) directory for more usage examples:
- [Weather Userbot](examples/weather-userbot/) - Simple userbot that provides weather information
- [Ayumax](examples/ayumax/) - Advanced userbot example

## Telegram bridge
See [telegram_bot/](telegram_bot/) and [implementation notes](TELEGRAM_BOT_IMPLEMENTATION_COMPLETE.md).
Local chat exports, sqlite state and secrets are intentionally **not** stored in this branch
(they live on `save_chats` only and are git-ignored here).

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author
**huxuxuya** - [huxuxuya@gmail.com](mailto:huxuxuya@gmail.com)

## Acknowledgments
- Original project by [nsdkinx](https://github.com/nsdkinx/vkmax)
- VK Group for developing the MAX messenger platform
