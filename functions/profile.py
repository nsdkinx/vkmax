from vkmax.client import MaxClient

async def change_online_status(client: MaxClient, hidden: bool):
    """ Hide or show you last online status. """
    return await client.invoke_method(22, {"settings":{"user":{"HIDDEN":hidden}}})

async def findable_by_phone(client: MaxClient, findable: bool):
    """ Changes your profile privacy settings. You can make your profile findable by phone or not. """
    findable = "ALL" if findable else "CONTACTS"
    return await client.invoke_method(22, {"settings":{"user":{"SEARCH_BY_PHONE":findable}}})

async def calls_privacy(client: MaxClient, findable: bool):
    """ You can enable or disable calls for everyone. """
    findable = "ALL" if findable else "CONTACTS"
    return await client.invoke_method(22, {"settings":{"user":{"INCOMING_CALL":findable}}})

async def get_devices(client: MaxClient):
    """ Returns information about sessions on account """
    return await client.invoke_method(96, {})
