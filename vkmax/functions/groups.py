from vkmax.client import MaxClient
from random import randint

async def create_group(
        client: MaxClient,
        group_name: str,
        participant_ids: list[int]
):
    """Creates a group"""
    return await client.invoke_method(
        opcode=64,
        payload={
              "message": {
                  "cid": randint(1750000000000, 2000000000000),  # TODO: fuck around and find out
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
