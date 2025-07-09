from vkmax.client import MaxClient

async def change_online_status_visibility(
        client: MaxClient,
        hidden: bool
    ):

    """ Hide or show you last online status """

    return await client.invoke_method(
        opcode = 22,
        payload = {
            "settings":
            {
                "user":
                {
                    "HIDDEN": hidden
                }
            }
        }
    )

async def set_is_findable_by_phone(
        client: MaxClient,
        findable: bool
    ):

    """ Changes your profile privacy settings. You can make your profile findable by phone or not. """
    
    findable = "ALL" if findable else "CONTACTS"
    return await client.invoke_method(
        opcode = 22,
        payload = {
            "settings":
            {
                "user":
                {
                    "SEARCH_BY_PHONE": findable
                }
            }
        }
    )

async def set_calls_privacy(
        client: MaxClient,
        can_be_called: bool
    ):

    """ You can enable or disable calls for everyone. """

    findable = "ALL" if can_be_called else "CONTACTS"
    return await client.invoke_method(
        opcode = 22,
        payload = {
            "settings":
            {
                "user":
                {
                    "INCOMING_CALL": findable
                }
            }
        }
    )

async def invite_privacy(
        client: MaxClient,
        invitable:  bool
    ):

    """ Changes privacy settings\nMakes possible or impossible inviting you to other chats """

    invitable = "ALL" if invitable else "CONTACTS"
    return await client.invoke_method(
        opcode = 22,
        payload = {
            "settings": {
                "user":
                {
                    "CHATS_INVITE": invitable
                }
            }
        }
    )

async def change_profile(
        client: MaxClient,
        first_name = None,
        last_name = None,
        bio = None
    ):

    """ Changes your public profile\nRecommended to use with all available options"""

    return await client.invoke_method(
        opcode = 16,
        payload = {
            "firstName": first_name,
            "lastName": last_name,
            "description": bio}
    )
    
