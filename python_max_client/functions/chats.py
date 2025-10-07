from typing import Optional
from vkmax.client import MaxClient

def get_chats(
    client: MaxClient,
    count: int = 40,
    chats_sync: int = 0,
    contacts_sync: int = 0,
    presence_sync: int = 0,
    drafts_sync: int = 0,
):

    cached_response = client.get_cached_chats()

    if cached_response is None:
        raise Exception(
            "No chats cached. Please call login_by_token() or sign_in() first. "
            "Chats are automatically loaded during login."
        )

    return cached_response

async def get_chat(
    client: MaxClient,
    chat_id: int,
    from_message_id: Optional[int] = None,
    forward: int = 30,
    backward: int = 30,
    get_messages: bool = True,
):

    import time

    # If from_message_id is not provided, use current timestamp in milliseconds
    # This tells API to load messages around current time (i.e., latest messages)
    if from_message_id is None:
        from_message_id = int(time.time() * 1000)

    payload = {
        "chatId": chat_id,
        "from": from_message_id,
        "forward": forward,
        "backward": backward,
        "getMessages": get_messages,
    }

    return await client.invoke_method(
        opcode=49,
        payload=payload,
    )


async def get_chat_messages(
    client: MaxClient,
    chat_id: int,
    count: int = 30,
    from_message_id: Optional[int] = None,
):

    return await get_chat(
        client=client,
        chat_id=chat_id,
        from_message_id=from_message_id,
        forward=0,  # Don't load forward when paginating backward
        backward=count,
        get_messages=True,
    )


async def mark_chat_as_read(
    client: MaxClient, chat_id: int, message_id: int, mark: Optional[int] = None
):

    import time

    if mark is None:
        mark = int(time.time() * 1000)

    return await client.invoke_method(
        opcode=50,
        payload={
            "type": "READ_MESSAGE",
            "chatId": chat_id,
            "messageId": str(message_id),
            "mark": mark,
        },
    )

async def mark_chat_as_unread(
    client: MaxClient, chat_id: int, mark: Optional[int] = None
):

    import time

    if mark is None:
        mark = int(time.time() * 1000)

    return await client.invoke_method(
        opcode=50, payload={"type": "SET_AS_UNREAD", "chatId": chat_id, "mark": mark}
    )

async def mute_chat(client: MaxClient, chat_id: int, forever: bool = True):

    dont_disturb = -1 if forever else 0

    return await client.invoke_method(
        opcode=22,
        payload={
            "settings": {"chats": {str(chat_id): {"dontDisturbUntil": dont_disturb}}}
        },
    )

async def leave_chat(client: MaxClient, chat_id: int):

    return await client.invoke_method(
        opcode=75, payload={"chatId": chat_id, "subscribe": False}
    )


async def join_chat(client: MaxClient, link: str):

    return await client.invoke_method(opcode=57, payload={"link": link})
