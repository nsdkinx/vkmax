import asyncio
import logging
import sys
from random import randint

from vkmax.client import MaxClient
from vkmax.features.messages import ayumax_callback
# from vkmax.features.users import resolve_users, add_to_contacts
from vkmax.features.groups import create_group

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
    await create_group(client, "ЭКСТЕРАГРАМ ОБНОВИЛСЯ!!!", [participant_id])
    await client.set_callback(ayumax_callback)
    await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
