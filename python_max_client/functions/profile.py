from vkmax.client import MaxClient
from typing import Optional


async def change_online_status_visibility(
    client: MaxClient,
    hidden: bool
):
    """Hide or show you last online status"""

    return await client.invoke_method(
        opcode=22,
        payload={
            "settings": {
                "user": {
                    "HIDDEN": hidden
                }
            }
        }
    )


async def set_is_findable_by_phone(
    client: MaxClient,
    findable: bool
):
    """You can make your profile findable by phone or not"""
    
    findable = "ALL" if findable else "CONTACTS"

    return await client.invoke_method(
        opcode=22,
        payload={
            "settings": {
                "user": {
                    "SEARCH_BY_PHONE": findable
                }
            }
        }
    )

async def set_calls_privacy(
    client: MaxClient,
    can_be_called: bool
):
    """You can enable or disable calls for everyone"""

    can_be_called = "ALL" if can_be_called else "CONTACTS"

    return await client.invoke_method(
        opcode = 22,
        payload = {
            "settings": {
                "user": {
                    "INCOMING_CALL": can_be_called
                }
            }
        }
    )


async def invite_privacy(
    client: MaxClient,
    invitable:  bool
):

    """Changes the possibility of inviting you to other chats"""

    invitable = "ALL" if invitable else "CONTACTS"

    return await client.invoke_method(
        opcode=22,
        payload={
            "settings": {
                "user": {
                    "CHATS_INVITE": invitable
                }
            }
        }
    )


async def change_profile(
    client: MaxClient,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    bio: Optional[str] = None
):
    """Changes your public profile"""

    return await client.invoke_method(
        opcode=16,
        payload={
            "firstName": first_name,
            "lastName": last_name,
            "description": bio
        }
    )
