from io import BufferedIOBase

import aiohttp
from vkmax.client import MaxClient, USER_AGENT


async def upload_photo(
        client: MaxClient,
        chat_id: int,
        stream: BufferedIOBase,
    ) -> dict:

    """Uploads one photo from the provided I/O stream

    Returns an attachment object that you can put into a list
    of attachments in vkmax.functions.messages"""

    resp = await client.invoke_method(
        opcode=80,
        payload={
            "count": 1
        }
    )

    upload_url = resp["payload"]["url"]
    del resp

    await client.invoke_method(
        opcode=65,
        payload={
            "chatId": chat_id,
            "type": "PHOTO"
        }
    )

    resp = await _upload(client, upload_url, stream)
    obj = await resp.json()
    token = list(obj['photos'].values())[0]['token']

    return {
        "_type": "PHOTO",
        "photoToken": token,
    }


async def upload_video(
        client: MaxClient,
        chat_id: int,
        stream: BufferedIOBase,
    ) -> dict:

    """Uploads one video"""

    resp = await client.invoke_method(
        opcode=82,
        payload={
            "count": 1
        }
    )
    info = resp["payload"]["info"][0]

    upload_url = info["url"]
    video_id = info["videoId"]
    token = info["token"]
    del info, resp

    await client.invoke_method(
        opcode=65,
        payload={
            "chatId": chat_id,
            "type": "VIDEO"
        }
    )

    await _upload(client, upload_url, stream)

    return {
        "_type": "VIDEO",
        "videoId": video_id,
        "token": token,
    }


async def _upload(
        client: MaxClient,
        url: str,
        stream: BufferedIOBase,
    ) -> aiohttp.ClientResponse:

    """Internal helper function"""

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.9',
        'Origin': 'https://web.max.ru',
        'Referer': 'https://web.max.ru/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': USER_AGENT,
    }

    if not client._http_pool:
        client._http_pool = aiohttp.ClientSession()

    with stream as file:
        data = aiohttp.FormData()
        data.add_field(
            'file', file,
            filename='image.jpg',
            content_type='image/jpeg',
        )

        resp = await client._http_pool.post(
            url,
            headers=headers,
            data=data,
        )
        resp.raise_for_status()

    # at this point formdata is already sent
    # (i hope so)
    return resp
