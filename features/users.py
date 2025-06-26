import logging
from vkmax.client import MaxClient

_logger = logging.getLogger(__name__)

async def resolve_users(client: MaxClient, user_id: list):
    """ Resolving users via userid"""
    return await client.invoke_method(32, {"contactIds":user_id})

async def add_to_contacts(client: MaxClient, user_id: int):
    """ Adding user to contacts via userid """
    return await client.invoke_method(34, {"contactId":user_id,"action":"ADD"})
