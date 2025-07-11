from vkmax.client import MaxClient
from random import randint

async def create_group(
        client: MaxClient,
        group_name: str,
        participant_ids: list[int]
    ):
    
    """ Creates a group """
    
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

async def invite_users(
        client: MaxClient,
        group_id: int,
        participant_ids: list[int],
        show_history = True
    ):
    
    """ Invites users into group via userid """
    
    return await client.invoke_method(
        opcode=77,
        payload={
            "chatId": group_id,
            "userIds": participant_ids,
            "showHistory": show_history,
            "operation": "add"
            }
        )

async def remove_users(
        client: MaxClient,
        group_id: int,
        participant_ids: list[int],
        delete_messages = False
    ):
    delete_messages = 0 if delete_messages == False else -1
    
    """ Removes users from group via userid """
    
    return await client.invoke_method(
        opcode=77,
        payload={
            "chatId":group_id,
            "userIds":participant_ids,
            "operation":"remove",
            "cleanMsgPeriod":delete_messages
            }
        )

async def add_admin(
        client: MaxClient,
        group_id: int,
        admin_ids = list[int],
        deleting_messages = False,
        control_participants = False,
        control_admins = False
    ):

    """ Adds an admin to group\nYou need to be a group owner or administrator with appropriate permissions to use this method. """
    
    # minimal admin: 120, minimal admin + deleting msgs: 121, minimal admin + deleting msgs + participants: 123, full_admin: 255, minimal admin + set_admins: 124, minimal admin + set_admins + deleting msgs: 125, minimal admin + set_admins + participants: 254, minimal admin + participants: 250, minimal admin + deletings msgs + participants: 251
    permissions = 120 if deleting_messages == False and control_participants == False and control_admins == False else ...
    permissions = 121 if deleting_messages == True and control_participants == False and control_admins == False else ...
    permissions = 123 if deleting_messages == True and control_participants == True and control_admins == False else ...
    permissions = 124 if deleting_messages == False and control_participants == False and control_admins == True else ...
    permissions = 125 if deleting_messages == True and control_participants == False and control_admins == True else ...
    permissions = 250 if deleting_messages == False and control_participants == True and control_admins == False else ...
    permissions = 251 if deleting_messages == True and control_participants == True and control_admins == False else ...
    permissions = 254 if deleting_messages == False and control_participants == True and control_admins == True else ...
    permissions = 255 if deleting_messages == True and control_participants == True and control_admins == True else ...
    
    return await client.invoke_method(
        opcode=77,
        payload = {
            "chatId":group_id,
            "userIds":admin_ids,
            "type":"ADMIN",
            "operation":"remove",
            "permissions": permissions
            }
    )

async def remove_admin(
        client: MaxClient,
        group_id: int,
        admin_ids = list[int]
    ):

    """ Removes an admin from group\nYou need to be a group owner or administrator with appropriate permissions to use this method. """
    
    return await client.invoke_method(
        opcode=77,
        payload = {
            "chatId":group_id,
            "userIds":admin_ids,
            "type":"ADMIN",
            "operation":"remove"
            }
    )

async def transfer_group_ownership(
        client: MaxClient, 
        group_id: int,
        new_owner_id: int
    ):

    """ Transfers ownership of the group to a new user """

    return await client.invoke_method(
        opcode=55,
        payload = {
            "chatId":group_id,
            "changeOwnerId":new_owner_id
            }
    )

async def change_group_settings(
        client: MaxClient,
        group_id : int,
        all_can_pin_message = False,
        only_owner_can_change_icon_title = True,
        only_admin_can_add_member = True

    ):

    """ Changes basic group settings """

    return await client.invoke_method(
        opcode=55,
        payload = {
            "chatId": group_id,
            "options": {
                "ONLY_OWNER_CAN_CHANGE_ICON_TITLE": only_owner_can_change_icon_title,
                "ALL_CAN_PIN_MESSAGE": all_can_pin_message,
                "ONLY_ADMIN_CAN_ADD_MEMBER": only_admin_can_add_member
                }
            }
    )

async def change_group_profile(
        client: MaxClient,
        group_id: int,
        new_group_name: str,
        new_description = None
    ): 

    """ Just changes a group public profile """

    if new_description != None:
        return await client.invoke_method(
            opcode=55,
            payload = {
                "chatId": group_id,
                "theme": new_group_name,
                }
        )
    
    else:
        return await client.invoke_method(
        opcode=55,
        payload = {
            "chatId": group_id,
            "theme": new_group_name,
            "description": new_description
            }
    )

async def get_group_members(
        client: MaxClient,
        group_id: int,
        marker = 0,
        count = 500
    ):

    """ Gets all the members in specified chat """

    if count > 500:
        raise Exception("Error while getting number of group members. Maximum available count is 500.")

    return await client.invoke_method(
        opcode = 59,
        payload = {
            "type":"MEMBER",
            "marker": marker,
            "chatId": group_id,
            "count": count
            }
    )
