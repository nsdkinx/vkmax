import asyncio
import itertools
import json
import logging
import uuid
from typing import Any, Callable, Optional

import aiohttp
import websockets
from websockets.asyncio.client import ClientConnection

from functools import wraps

WS_HOST = "wss://ws-api.oneme.ru/websocket"
RPC_VERSION = 11
APP_VERSION = "25.12.13"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"

_logger = logging.getLogger(__name__)


def ensure_connected(method: Callable):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if self._connection is None:
            raise RuntimeError("WebSocket not connected. Call .connect() first.")
        return method(self, *args, **kwargs)

    return wrapper


class MaxClient:
    def __init__(self):
        self._connection: Optional[ClientConnection] = None
        self._http_pool: Optional[aiohttp.ClientSession] = None
        self._is_logged_in: bool = False
        self._device_id: Optional[str] = None
        self._seq = itertools.count(1)
        self._keepalive_task: Optional[asyncio.Task] = None
        self._recv_task: Optional[asyncio.Task] = None
        self._incoming_event_callback = None
        self._reconnect_callback = None
        self._pending = {}
        self._video_pending = {}
        self._file_pending = {}

    # --- WebSocket connection management ---

    async def connect(self):
        if self._connection:
            raise Exception("Already connected")

        _logger.info(f'Connecting to {WS_HOST}...')
        self._connection = await websockets.connect(
            WS_HOST,
            origin=websockets.Origin('https://web.max.ru'),
            user_agent_header=USER_AGENT
        )

        self._recv_task = asyncio.create_task(self._recv_loop())
        _logger.info('Connected. Receive task started.')
        return self._connection

    @ensure_connected
    async def disconnect(self):
        await self._stop_keepalive_task()
        self._recv_task.cancel()
        await self._connection.close()
        self._connection = None
        if self._http_pool:
            await self._http_pool.close()
            self._http_pool = None

    @ensure_connected
    async def invoke_method(self, opcode: int, payload: dict[str, Any], retries: int = 2):
        seq = next(self._seq)

        request = {
            "ver": RPC_VERSION,
            "cmd": 0,
            "seq": seq,
            "opcode": opcode,
            "payload": payload
        }
        _logger.info(f'-> REQUEST: {request}')

        future = asyncio.get_event_loop().create_future()
        self._pending[seq] = future

        try:
            await self._connection.send(
                json.dumps(request)
            )
        except websockets.exceptions.ConnectionClosed:
            _logger.warning('got ws disconnect in invoke_method')
            if self._reconnect_callback:
                _logger.info('reconnecting')
                await self._reconnect_callback()
                if retries > 0:
                    _logger.info('retrying invoke_method after reconnect')
                    await self.invoke_method(opcode, payload, retries - 1)
            return

        response = await future
        _logger.info(f'<- RESPONSE: {response}')

        return response

    async def set_callback(self, function):
        import warnings
        warnings.warn('switch to set_packet_callback', category=DeprecationWarning)
        self.set_packet_callback(function)

    def set_packet_callback(self, function):
        if not asyncio.iscoroutinefunction(function):
            raise TypeError('callback must be async')
        self._incoming_event_callback = function

    def set_reconnect_callback(self, function):
        if not asyncio.iscoroutinefunction(function):
            raise TypeError('callback must be async')
        self._reconnect_callback = function

    async def _recv_loop(self):
        try:
            async for packet in self._connection:
                packet = json.loads(packet)

                seq = packet["seq"]
                future = self._pending.pop(seq, None)
                if future:
                    future.set_result(packet)
                    continue

                if packet.get("opcode") == 136:
                    payload = packet.get("payload", {})
                    future = None

                    if "videoId" in payload:
                        future = self._video_pending.pop(payload["videoId"], None)
                    elif "fileId" in payload:
                        future = self._file_pending.pop(payload["fileId"], None)

                    if future:
                        future.set_result(None)
                
                if self._incoming_event_callback:
                    asyncio.create_task(self._incoming_event_callback(self, packet))

        except asyncio.CancelledError:
            _logger.info(f'receiver cancelled')
            return

        except websockets.exceptions.ConnectionClosed:
            _logger.warning('got ws disconnect in receiver')
            if self._reconnect_callback:
                _logger.info('reconnecting')
                await self._reconnect_callback()

    # --- Keepalive system

    @ensure_connected
    async def _send_keepalive_packet(self):
        await self.invoke_method(
            opcode=1,
            payload={"interactive": False}
        )

    @ensure_connected
    async def _keepalive_loop(self):
        _logger.info(f'keepalive task started')
        try:
            while True:
                await self._send_keepalive_packet()
                await asyncio.sleep(30)
        except asyncio.CancelledError:
            _logger.info('keepalive task stopped')
            return

    @ensure_connected
    async def _start_keepalive_task(self):
        if self._keepalive_task:
            raise Exception('Keepalive task already started')

        self._keepalive_task = asyncio.create_task(self._keepalive_loop())
        return

    async def _stop_keepalive_task(self):
        if not self._keepalive_task:
            raise Exception('Keepalive task is not running')

        self._keepalive_task.cancel()
        self._keepalive_task = None
        return

    # --- Authentication ---

    @ensure_connected
    async def _send_hello_packet(self, device_id: Optional[str] = None):
        self._device_id = device_id or f'{uuid.uuid4()}'
        return await self.invoke_method(
            opcode=6,
            payload={
                "userAgent": {
                    "deviceType": "DESKTOP", 
                    "locale": "ru",
                    "deviceLocale": "ru",
                    "osVersion": "Linux",
                    "deviceName": "Chrome",
                    "headerUserAgent": USER_AGENT,
                    "appVersion": APP_VERSION,
                    "screen": "1080x1920 1.0x",
                    "timezone": "Europe/Moscow",
                    "clientSessionId": 14,
                    "buildNumber": 0x97CB
                },
                "deviceId": self._device_id,
            }
        )

    @ensure_connected
    async def send_code(self, phone: str) -> str:
        """:returns: Login token."""
        await self._send_hello_packet()
        start_auth_response = await self.invoke_method(
            opcode=17,
            payload={
                "phone": phone,
                "type": "START_AUTH",
                "language": "ru"
            }
        )
        return start_auth_response["payload"]["token"]

    @ensure_connected
    async def sign_in(self, sms_token: str, sms_code: int):
        """
        Auth token for further login is at ['payload']['tokenAttrs']['LOGIN']['token']
        :param login_token: Must be obtained via `send_code`.
        """
        verification_response = await self.invoke_method(
            opcode=18,
            payload={
                "token": sms_token,
                "verifyCode": str(sms_code),
                "authTokenType": "CHECK_CODE"
            }
        )

        if "error" in verification_response["payload"]:
            raise Exception(verification_response["payload"]["error"])

        try:
            phone = verification_response["payload"]["profile"]["contact"]["phone"]
        except:
            phone = '[?]'
            _logger.warning('Got no phone number in server response')
        _logger.info(f'Successfully logged in as {phone}')

        self._is_logged_in = True
        await self._start_keepalive_task()

        return verification_response

    @ensure_connected
    async def login_by_token(self, token: str, device_id: Optional[str] = None):
        await self._send_hello_packet(device_id)
        _logger.info("using session")
        login_response = await self.invoke_method(
            opcode=19,
            payload={
                "interactive": True,
                "token": token,
                "chatsSync": 0,
                "contactsSync": 0,
                "presenceSync": 0,
                "draftsSync": 0,
                "chatsCount": 40,
                "userAgent": {
                    "deviceType": "DESKTOP", 
                    "locale": "ru",
                    "deviceLocale": "ru",
                    "osVersion": "Linux",
                    "deviceName": "Chrome",
                    "headerUserAgent": USER_AGENT,
                    "appVersion": APP_VERSION,
                    "screen": "1080x1920 1.0x",
                    "timezone": "Europe/Moscow",
                    "clientSessionId": 14,
                    "buildNumber": 0x97CB
                }
            }
        )

        if "error" in login_response["payload"]:
            raise Exception(login_response["payload"]["error"])

        try:
            phone = login_response["payload"]["profile"]["contact"]["phone"]
        except:
            phone = '[?]'
            _logger.warning('Got no phone number in server response')
        _logger.info(f'Successfully logged in as {phone}')

        self._is_logged_in = True
        await self._start_keepalive_task()

        return login_response

    @property
    def device_id(self) -> Optional[str]:
        return self._device_id
