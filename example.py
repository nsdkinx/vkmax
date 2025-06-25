import asyncio
import logging
import sys

from vkmax.client import MaxClient

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

async def ayumax_callback(packet: dict):
    if packet['opcode'] == 128:
        message_text = packet['payload']['message']['text']

        if (
            'status' in packet['payload']['message']
            and packet['payload']['message']['status'] == "REMOVED"
        ):
            print(f'Got deleted message {message_text}. Аюграм в 100 метрах от вас')

        else:
            print(f'Incoming message! {message_text}')

async def main():
    client = MaxClient()
    await client.connect()
    await client.login_by_token("your token")
    client.set_callback(ayumax_callback)
    await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
