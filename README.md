# vkmax
Python user client for VK MAX messenger (OneMe) with userbot and ToS avoiding features

## What is VK MAX?
MAX (internal code name OneMe) is another project by the Russian government in an attempt to create a unified domestic messaging platform with features such as login via the government services account (Gosuslugi/ESIA).  
It is developed by VK Group.  
As usual, the application is extremely poorly made: all your contacts, login info and private messages are sent over the network in plain text without any encryption (besides TLS).

## Protocol
The packet consists of five JSON fields:
* `ver` (int) - currently it's 11
* `cmd` (int[0, 1]) - 0 for outgoing packets, 1 for incoming packets
* `opcode` (int) - RPC method ID
* `payload` (json) - arbitrary

## Authorization flow
0. Connect to websocket `wss://ws-api.oneme.ru/websocket`
1. Send hello packet:
   ```python
   {
    "userAgent": {
        "deviceType": "WEB",
        "locale": "ru_RU",
        "osVersion": "macOS",
        "deviceName": "vkmax Python",
        "headerUserAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "deviceLocale": "ru-RU",
        "appVersion": APP_VERSION,
        "screen": "956x1470 2.0x",
        "timezone": "Asia/Vladivostok"
       },
    "deviceId": str(uuid.uuid4())
   }
   ```
3. Start auth:
   ```python
   {
       "ver":11,
       "cmd":0,
       "seq":1,
       "opcode":17,
       "payload":{
          "phone":"phone",
          "type":"START_AUTH",
          "language":"ru"
       }
    }
   ```
   After that websocket sends a packet with sms_token to client
4. Confirm SMS code:
   ```python
   {
    "token": sms_token,
    "verifyCode": str(sms_code),
    "authTokenType": "CHECK_CODE"
   }
   ```
   Now you are logged in.
## Client flow
Baseline packet looks like:
```python
{
   "ver": RPC_VERSION,
   "cmd": 0, 
   "seq": seq,
   "opcode": opcode,
   "payload": payload
}
```
Known opcodes are listed in `opcodes.md` file.\
Example of using baseline packet to send message:
```python
{
  "ver": 11,
  "cmd": 0,
  "seq": seq,
  "opcode": 64,
  "payload": {
    "chatId": to_chat_id,
    "message": {
      "text": "text you need to send",
      "cid": 175xxxxxxxxxx,
      "elements": [],
      "attaches": []
    },
    "notify": true
  }
}
```

