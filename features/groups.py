import logging
from vkmax.client import MaxClient
from random import randint

_logger = logging.getLogger(__name__)

async def create_group(client: MaxClient, group_name: str, participant_ids: list):
    """Creates a group"""
    return await client.invoke_method(64, 
      {
        "message": {
          "cid": randint(1750000000000, 2000000000000),
          "attaches": [
            {
              "_type": "CONTROL",
              "event": "new",
              "chatType": "CHAT",
              "title": group_name,
              "userIds": participant_ids
            }
          ]
        },
        "notify": True
      }
    )
