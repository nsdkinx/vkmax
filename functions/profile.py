from vkmax.client import MaxClient

async def change_online_status(client: MaxClient, hidden: bool):
    """ Hide or show your last online status """
    return await client.invoke_method(22, {"settings":{"user":{"HIDDEN":hidden}}})
