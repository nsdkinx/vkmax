from vkmax.client import MaxClient


async def resolve_users(
    client: MaxClient,
    user_id: list
):
    """Resolving users via userid"""

    return await client.invoke_method(
        opcode=32,
        payload={
            "contactIds":user_id
        }
    )


async def add_to_contacts(client: MaxClient, user_id: int):
    """Adding user to contacts via userid"""

    return await client.invoke_method(
        opcode=34,
        payload={
            "contactId":user_id,
            "action":"ADD"
        }
    )


async def ban(client: MaxClient, user_id: int):
    """Banhammer to user's head"""

    return await client.invoke_method(
        opcode=34,
        payload={
            "contactId":user_id,
            "action":"BLOCK"
        }
    )
