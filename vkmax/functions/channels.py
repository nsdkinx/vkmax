from vkmax.client import MaxClient
from random import randint


async def resolve_channel_username(
    client: MaxClient, 
    username: str
):
    """Resolving channel by username"""

    return await client.invoke_method(
        opcode=89,
        payload={
            "link": f"https://max.ru/{username}"
        }
    )


async def resolve_channel_id(
    client: MaxClient,
    channel_id: int
):
    """Resolve channel by id"""

    return await client.invoke_method(
        opcode=48,
        payload={
            "chatIds": [channel_id]
        }
    )


async def join_channel(
    client: MaxClient,
    username: str
):
    """Joining a channel and resolving"""

    return await client.invoke_method(
        opcode=57,
        payload={
            "link": f"https://max.ru/{username}"
        }
    )


async def create_channel(
        client: MaxClient,
        channel_name: str
    ):
    return await client.invoke_method(
        opcode=64,
        payload={
            "message": {
                "cid": randint(1750000000000, 2000000000000),
                "attaches":
                    [
                        {
                            "_type": "CONTROL",
                            "event": "new",
                            "title": channel_name,
                            "chatType": "CHANNEL"
                        }
                    ],
                "text": ""
            }
        }
    )


async def mute_channel(
        client: MaxClient,
        channel_id: int,
        mute: bool = True
    ):
    """Mutes or unmutes a channel"""

    return await client.invoke_method(
        opcode=22,
        payload={
            "settings": {
                "chats": {
                    str(channel_id): {
                        "dontDisturbUntil": -1 if mute else 0
                    }
                }
            }
        }
    )
