import asyncio
from io import BufferedIOBase

import aiohttp
from vkmax.client import MaxClient, USER_AGENT


async def download_video(
        client: MaxClient,
        chat_id: int,
        message_id: str,
        video_id: int,
    ) -> str:

    """Requests a direct link to download the video"""

    resp = await client.invoke_method(
        opcode=83,
        payload={
            "videoId": video_id,
            "chatId": chat_id,
            "messageId": message_id
        }
    )

    formats = resp["payload"]
    del formats["cache"]
    del formats["EXTERNAL"]

    # return first url
    return list(formats.values())[0]


async def download_file(
        client: MaxClient,
        chat_id: int,
        message_id: str,
        file_id: int,
    ) -> str:

    """Requests a direct link to download the file"""

    resp = await client.invoke_method(
        opcode=88,
        payload={
            "fileId": file_id,
            "chatId": chat_id,
            "messageId": message_id
        }
    )
    return resp["payload"]["url"]


async def upload_photo(
        client: MaxClient,
        chat_id: int,
        stream: BufferedIOBase,
    ) -> dict:

    """Uploads one photo from the provided I/O stream

    Returns an attachment object to use in vkmax.functions.messages
    as a list item in `attaches` argument"""

    resp = await client.invoke_method(
        opcode=80,
        payload={
            "count": 1
        }
    )

    upload_url = resp["payload"]["url"]

    resp = await _upload(
        client,
        chat_id,
        upload_url,
        stream,
        attach_type="PHOTO",
        filename="image.jpg",
        mimetype="image/jpeg",
    )
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

    """Uploads one video from the provided I/O stream

    Returns an attachment object to use in vkmax.functions.messages
    as a list item in `attaches` argument"""

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

    await _upload(
        client,
        chat_id,
        upload_url,
        stream,
        attach_type="VIDEO",
        filename="video.mp4",
        mimetype="video/mp4",
    )

    future = asyncio.get_running_loop().create_future()
    client._video_pending[video_id] = future
    await future

    return {
        "_type": "VIDEO",
        "videoId": video_id,
        "token": token,
    }


async def upload_file(
        client: MaxClient,
        chat_id: int,
        stream: BufferedIOBase,
        filename: str = "file.bin"
    ) -> dict:

    """Uploads one file from the provided I/O stream

    Returns an attachment object to use in vkmax.functions.messages
    as a list item in `attaches` argument"""

    resp = await client.invoke_method(
        opcode=87,
        payload={
            "count": 1
        }
    )

    info = resp["payload"]["info"][0]

    upload_url = info["url"]
    file_id = info["fileId"]

    del info, resp

    await _upload(
        client,
        chat_id,
        upload_url,
        stream,
        attach_type="FILE",
        filename=filename,
        mimetype="application/octet-stream",
    )

    future = asyncio.get_running_loop().create_future()
    client._file_pending[file_id] = future
    await future

    return {
        "_type": "FILE",
        "fileId": file_id,
    }


async def _upload(
        client: MaxClient,
        chat_id: int,
        url: str,
        stream: BufferedIOBase,
        attach_type: str,
        filename: str,
        mimetype: str,
    ) -> aiohttp.ClientResponse:

    """Internal helper function"""

    await client.invoke_method(
        opcode=65,
        payload={
            "chatId": chat_id,
            "type": attach_type,
        }
    )

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
            filename=filename,
            content_type=mimetype,
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
