from Maxon.init import VERSION, START_TIME

import random

__name__ = "Pickme"
__description__ = "Pickme messages <3"
__version__ = "1.0.0"
__author__ = "@nerkux"

async def handle(packet, args):

    emojis = ["✨", "❤️‍🔥", "🔥", "🎀", "🍓", "🌺"]

    originalText = " ".join(args)
    modifiedText = " ".join(
        word + (f" {random.choice(emojis)}" if random.random() > 0 else "")
        for word in originalText.split()
    )
    return modifiedText

def register(handlers):
    handlers[".pickme"] = handle
