# vkmax
Python client for VK MAX messenger (OneMe)

## What is VK MAX?
MAX (internal code name OneMe) is another bullshit project by the Russian government in an attempt to create a unified domestic messaging platform with features such as login via the government services account (Gosuslugi/ESIA).  
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
1. Start auth:
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
... to be filled
