import logging
import python_weather

from vkmax.client import MaxClient
from vkmax.functions.messages import edit_message

_logger = logging.getLogger(__name__)

async def userbot(client: MaxClient, packet: dict):
    """ Userbot for vkmax """
    if packet['opcode'] == 128:
        cmd = packet['payload']['message']['text']
        if cmd == ".info":
            text = "Userbot connected"
            await edit_message(client, packet["payload"]["chatId"], packet["payload"]["message"]["id"], text)
        elif ".weather" in cmd:
            town = cmd.split(" "); town = town[1]
            async with python_weather.Client(unit=python_weather.METRIC, locale=python_weather.Locale.RUSSIAN) as weather_client:
                weather = await weather_client.get(town)
                builder = f"🌡️ Температура: {weather.temperature}°\n😶‍🌫️ Ощущается как: {weather.feels_like}°"
                await edit_message(client, packet["payload"]["chatId"], packet["payload"]["message"]["id"], builder)

                



