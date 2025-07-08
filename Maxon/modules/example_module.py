from Maxon.init import VERSION, START_TIME

async def handle(packet, args):
    return "example answer"

def register(handlers):
    handlers[".example"] = handle
