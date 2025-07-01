import asyncio
import logging
import sys

from vkmax.client import MaxClient
from Maxon.userbot.init import packet_callback, load_command_modules

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
    # client connection
    client = MaxClient()
    await client.connect()

    # logging in
    try:
        await client.start("phone_number")
    except:
        raise Exception("Phone number must be set!")

    # userbot started
    await load_command_modules()
    await client.set_callback(packet_callback)

    await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
