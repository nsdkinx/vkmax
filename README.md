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

### Requirements
- Python 3.9 or higher
- Internet connection for VK MAX messenger access

### Dependencies
The package automatically installs the following dependencies:
- `websockets>=12.0` - WebSocket client for real-time communication
- `httpx>=0.25.0` - HTTP client for API requests

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
import requests
from python_max_client import MaxClient
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

## API Reference

### MaxClient
The main client class for interacting with VK MAX messenger.

```python
from python_max_client import MaxClient

client = MaxClient()
```

#### Methods
- `connect()` - Connect to VK MAX servers
- `send_code(phone)` - Send SMS code to phone number
- `sign_in(token, code)` - Sign in with SMS code
- `login_by_token(token)` - Login with saved token
- `set_callback(callback)` - Set message handler callback

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

- `python_max_client.functions.messages` - Message operations
- `python_max_client.functions.users` - User management
- `python_max_client.functions.groups` - Group operations
- `python_max_client.functions.chats` - Chat management
- `python_max_client.functions.channels` - Channel operations
- `python_max_client.functions.profile` - Profile management

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
