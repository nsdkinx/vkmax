import asyncio
import logging
import sys

from vkmax.client import MaxClient
from vkmax.features.messages import ayumax_callback, get_deleted_messages

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
    # await client.login_by_token("token") # maybe you have a token ?
    # get_token = await client.start_sms_login("phone_number") # if you want to login manually
    # sms_code = int(input("Input SMS code: "))
    # await client.finish_sms_login(get_token, sms_code)
    await client.start("phone_number") # logging in via terminal
    print(await get_deleted_messages(chat_id=123))
    client.set_callback(ayumax_callback)
    await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
