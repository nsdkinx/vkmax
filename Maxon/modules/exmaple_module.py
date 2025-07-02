async def handle(packet):
    return "example answer"

def register(handlers):
    handlers[".example"] = handle
