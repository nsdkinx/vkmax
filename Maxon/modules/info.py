from Maxon.userbot.init import VERSION, START_TIME

import platform
import socket
import json
import time
from datetime import datetime, UTC
from pathlib import Path

SETTINGS_PATH = Path(__file__).parent / "userdata" / "settings.json"

async def handle(packet, args):
    uptime_seconds = int(time.time() - START_TIME)
    uptime_str = str(datetime.fromtimestamp(uptime_seconds, UTC).strftime("%H:%M:%S"))

    host_name = socket.gethostname()
    system = platform.system()
    release = platform.release()
    python_version = platform.python_version()
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if SETTINGS_PATH.exists():
        with open(SETTINGS_PATH, encoding="utf-8") as f:
            data = json.load(f)
            bio = data.get("bio")
    else:
        bio = "Not set"

    return (
        f"🛠 Maxon Info\n"
        f"\n"
        f"🌐 Host: {host_name} ({system} {release})\n"
        f"🐍 Python: {python_version}\n"
        f"🕒 Time: {time_now}\n"
        f"⚙️ Version: {VERSION}\n"
        f"📈 Uptime: {uptime_str}\n"
        "\n"
        f"{bio}"
    )

def register(handlers):
    handlers[".info"] = handle
