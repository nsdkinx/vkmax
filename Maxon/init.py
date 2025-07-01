import asyncio
import logging
import requests
import sys
import time
from typing import Callable, Dict, Any
from importlib import import_module

from vkmax.client import MaxClient
from functions.messages import edit_message

from pathlib import Path

date_format = '%d.%m.%Y %H:%M:%S'
logging_format = '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'
MODULES_DIR = Path(__file__).parent / "modules"
VERSION = "1.1"
START_TIME = time.time()
handlers = [logging.StreamHandler(sys.stdout)]

logging.basicConfig(
    format=logging_format,
    datefmt=date_format,
    handlers=handlers,
    level=logging.INFO
)

command_handlers: Dict[str, Callable[[dict, list[str]], str]] = {}

sys.path.append(str(MODULES_DIR.parent))

command_handlers = {}

async def load_command_modules():

    for file_path in MODULES_DIR.glob("*.py"):
        if file_path.name.startswith("__"):
            continue

        module_name = file_path.stem
        try:
            import_path = f"{MODULES_DIR.name}.{module_name}"
            module = import_module(import_path)

            if hasattr(module, "register"):
                module.register(command_handlers)
                logging.info(f"Registered command from: {module_name}")
            else:
                raise Exception(f"Module {module_name} has no 'register' function")

        except Exception as e:
            raise Exception(f"Failed to import {module_name}: {e}")


async def packet_callback(client: MaxClient, packet: dict):
    if packet['opcode'] != 128:
        return
    
    message_text: str = packet['payload']['message']['text']
    command = message_text.split()[0]
    args = message_text.split()[1:]
    handler = command_handlers.get(command)

    if handler:
        text = await handler(packet, args)
        await edit_message(
            client,
            packet["payload"]["chatId"],
            packet["payload"]["message"]["id"],
            text
        )

