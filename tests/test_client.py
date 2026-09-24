"""
Tests for MaxClient (offline, no network).

Supports both package layouts:
- main branch:        python_max_client/
- save_chats branch:  vkmax/
Local repo code is preferred over any installed distribution.
"""

import asyncio
import inspect
import pathlib
import warnings
from unittest.mock import AsyncMock

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

if (REPO_ROOT / "python_max_client" / "client.py").is_file():
    PKG = "python_max_client"
elif (REPO_ROOT / "vkmax" / "client.py").is_file():
    PKG = "vkmax"
else:  # fallback to installed distribution
    PKG = "python_max_client"

from importlib import import_module  # noqa: E402

client_mod = import_module(f"{PKG}.client")
messages_mod = import_module(f"{PKG}.functions.messages")
uploads_mod = import_module(f"{PKG}.functions.uploads")

MaxClient = client_mod.MaxClient


def make_client(**kwargs):
    client = MaxClient(**kwargs) if kwargs else MaxClient()
    client.invoke_method = AsyncMock(return_value={"payload": {}})
    return client


class TestMaxClientInit:
    def test_client_initialization(self):
        client = MaxClient()
        assert client is not None
        assert hasattr(client, "connect")
        assert hasattr(client, "login_by_token")
        assert hasattr(client, "send_code")
        assert hasattr(client, "sign_in")

    def test_new_state_attrs_from_merge(self):
        """Attrs from both sides of the upstream merge must exist."""
        client = MaxClient()
        # fork side: chats cache
        assert hasattr(client, "_cached_chats")
        assert client.get_cached_chats() is None
        # upstream side: pending upload futures
        assert hasattr(client, "_video_pending")
        assert hasattr(client, "_file_pending")
        # upstream side: device id property
        assert client.device_id is None

    def test_methods_exist_and_callable(self):
        client = MaxClient()
        for name in ("connect", "disconnect", "login_by_token",
                     "send_code", "sign_in", "invoke_method",
                     "set_packet_callback", "set_reconnect_callback"):
            assert callable(getattr(client, name)), name


class TestCallbacks:
    @pytest.mark.asyncio
    async def test_set_callback_deprecated_async_wrapper(self):
        """set_callback is async (deprecated); must be awaited with async fn."""
        client = MaxClient()

        async def cb(client, packet):
            pass

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            await client.set_callback(cb)
        assert client._incoming_event_callback is cb

    def test_set_packet_callback_rejects_sync(self):
        client = MaxClient()

        def sync_cb(client, packet):
            pass

        with pytest.raises(TypeError):
            client.set_packet_callback(sync_cb)

    def test_set_packet_callback_accepts_async(self):
        client = MaxClient()

        async def cb(client, packet):
            pass

        client.set_packet_callback(cb)
        assert client._incoming_event_callback is cb

    def test_set_reconnect_callback_validation(self):
        client = MaxClient()

        async def cb():
            pass

        client.set_reconnect_callback(cb)
        assert client._reconnect_callback is cb

        with pytest.raises(TypeError):
            client.set_reconnect_callback(lambda: None)


class TestMessagesApi:
    def test_send_message_signature(self):
        sig = inspect.signature(messages_mod.send_message)
        assert "reply_to" in sig.parameters
        assert "attaches" in sig.parameters

    def test_edit_message_signature(self):
        sig = inspect.signature(messages_mod.edit_message)
        assert "attaches" in sig.parameters

    def test_helpers_exist(self):
        for name in ("send_message", "edit_message", "delete_message",
                     "pin_message", "reply_message", "send_photo", "send_file"):
            assert callable(getattr(messages_mod, name)), name

    @pytest.mark.asyncio
    async def test_send_message_payload_with_reply_and_attaches(self):
        client = make_client()
        attach = {"_type": "PHOTO", "photoToken": "tok"}
        await messages_mod.send_message(
            client, chat_id=123, text="hi",
            reply_to=456, attaches=[attach],
        )
        assert client.invoke_method.await_count == 1
        kwargs = client.invoke_method.call_args[1]
        opcode, payload = kwargs["opcode"], kwargs["payload"]
        assert opcode == 64
        assert payload["chatId"] == 123
        assert payload["message"]["attaches"] == [attach]
        assert payload["message"]["link"] == {"type": "REPLY", "messageId": "456"}

    @pytest.mark.asyncio
    async def test_send_message_payload_without_reply(self):
        client = make_client()
        await messages_mod.send_message(client, chat_id=1, text="hi")
        payload = client.invoke_method.call_args[1]["payload"]
        assert "link" not in payload["message"]
        assert payload["message"]["attaches"] == []


class TestUploadsApi:
    def test_upload_functions_exist(self):
        for name in ("download_video", "download_file",
                     "upload_photo", "upload_video", "upload_file"):
            assert callable(getattr(uploads_mod, name)), name

    @pytest.mark.asyncio
    async def test_download_file_uses_opcode_88(self):
        client = make_client()
        client.invoke_method = AsyncMock(
            return_value={"payload": {"url": "https://example/file"}})
        url = await uploads_mod.download_file(
            client, chat_id=1, message_id="m1", file_id=42)
        assert url == "https://example/file"
        assert client.invoke_method.call_args[1]["opcode"] == 88
