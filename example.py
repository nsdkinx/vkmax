import asyncio
import logging
import sys

from vkmax.client import MaxClient
from vkmax.functions.messages import send_message
from vkmax.features.userbot.userbot import userbot

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

async def main():
    client = MaxClient()
    await client.connect()
    await client.start("phone_number")

    await send_message(client, chat_id=123, text="Cнег растаял на плечах... твоей шубы норковой")
    await client.set_callback(userbot)

    await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
