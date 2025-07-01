import asyncio
import logging
import sys
from pathlib import Path

from vkmax.client import MaxClient
from Maxon.init import packet_callback, load_command_modules

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

    login_token_file = Path('login_token.txt')

    if login_token_file.exists():
        login_token_from_file = login_token_file.read_text(encoding='utf-8').strip()
        try:
            await client.login_by_token(login_token_from_file)
        except:
            print("Couldn't login by token. Falling back to SMS login")

    else:
        sms_login_token = await client.send_code('phone_number')
        sms_code = int(input('Enter SMS code: '))
        account_data = await client.sign_in(sms_login_token, sms_code)

        login_token = account_data['payload']['tokenAttrs']['LOGIN']['token']
        login_token_file.write_text(login_token, encoding='utf-8')

    await load_command_modules()
    await client.set_callback(packet_callback)

    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
