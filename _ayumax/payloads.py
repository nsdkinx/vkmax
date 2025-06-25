import time
import uuid

request_payload = {
    "ver": 11,
    "cmd": 0,
    "seq": 0,
    "opcode": 6,
    "payload": {
        "userAgent": {
            "deviceType": "WEB",
            "locale": "ru_RU",
            "osVersion": "macOS",
            "deviceName": "Огромный член Саши Мелентьева",
            "headerUserAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "deviceLocale": "ru-RU",
            "appVersion": "25.6.8",
            "screen": "956x1470 2.0x",
            "timezone": "Asia/Vladivostok"
        },
        "deviceId": str(uuid.uuid4())
    }
}

shit_payload = {"ver":11,"cmd":0,"seq":1,"opcode":1,"payload":{"interactive":False}}

async def login_payload(phone: str):
    return {"ver":11,"cmd":0,"seq":1,"opcode":17,"payload":{"phone":phone,"type":"START_AUTH","language":"ru"}}

async def sms_code_payload(code: str, token: str):
    return {"ver":11,"cmd":0,"seq":2,"opcode":18,"payload":{"token":token,"verifyCode":code,"authTokenType":"CHECK_CODE"}}

async def token_payload(token: str):
    return {"ver":11,"cmd":0,"seq":1,"opcode":19,"payload":{"interactive":True,"token":token,"chatsSync":0,"contactsSync":0,"presenceSync":0,"draftsSync":0,"chatsCount":40}}

async def token_start_payload(session_id: str):
    return {"ver":11,"cmd":0,"seq":1,"opcode":5,"payload":{"events":[{"type":"NAV","event":"COLD_START","userId":-1,"time":int(time.time()),"params":{"session_id":session_id,"action_id":1,"screen_to":1}}]}}
