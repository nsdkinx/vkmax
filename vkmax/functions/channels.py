from vkmax.client import MaxClient

async def resolve_channel(
        client: MaxClient, 
        username: str
    ):

    """ Only channel resolving """

    await client.invoke_method(
        opcode = 89,
        payload = {
            "link": f"https://max.ru/{username}"
            }
    )

async def join_channel(
        client: MaxClient,
        username: str
    ):

    """ Joining a channel and resolving """

    await client.invoke_method(
        opcode = 57,
        payload = {
            "link": f"https://max.ru/{username}"
        }
    )

