import asyncio
import websockets
import json
import os
from payloads import *
from modules import *

WS_URL = "wss://ws-api.oneme.ru/websocket"

async def handle_message(message: str):
    print(message)
    try:
        data = json.loads(message)
    except TypeError:
        print(message, 'unhandled')

    if "message" in data["payload"]:
        if data["payload"]["message"] == "REMOVED":
            print("Обнаружено удалённое сообщение!", f"\n{data["payload"]["message"]["text"]}")
        if "status" not in data["payload"]["message"]:
            print("Новое сообщение: ", data["payload"]["message"]["text"])
    else:
        print("Мусорный пакет", message)

async def sms_login():
    async with websockets.connect(WS_URL) as websocket:
        # посылаем первый запрос
        await websocket.send(json.dumps(request_payload))
        first_response = await websocket.recv()

        # посылаем второй запрос (логин)
        phone_number = str(input("Введите номер телефона: (+7xxxxxxxxxx) "))
        await websocket.send(json.dumps(await login_payload(phone_number)))
        second_response = await websocket.recv(); second_response = json.loads(second_response)
        login_token = second_response["payload"]["token"]
        print("login_token", login_token)
        # await token_write(login_token)

        # посылаем третий запрос с смс кодом
        sms_code = str(input("Введите СМС код: "))
        await websocket.send(json.dumps(await sms_code_payload(sms_code, login_token)))
        user = await websocket.recv(); user = json.loads(user)
        token = user['payload']['tokenAttrs']['LOGIN']['token']
        await token_write(token)
        if "error" in user["payload"]:
            os.remove("token.txt")
            if user["payload"]["error"] == "error.code.attempt.limit":
                print("Слишком много попыток входа в аккаунт")
            else:
                print("Неизвестная ошибка: ", user["payload"]["error"])
        elif "profile" in user["payload"]:
            print(f"Успешный вход в аккаунт!\nИмя: {user["payload"]["profile"]["names"][0]["name"]}\nАйди: {user["payload"]["profile"]["id"]}\nНомер: {user["payload"]["profile"]["phone"]}")
            await websocket.send(json.dumps(shit_payload))
            message = await websocket.recv(); message = json.loads(message)
            if message["payload"] == None:
                message = await websocket.recv(); message = json.loads(message)
            await handle_message(message)

async def token_login():
    async with websockets.connect(WS_URL) as websocket:
        # посылаем первый запрос
        await websocket.send(json.dumps(request_payload))
        first_response = await websocket.recv()

        # посылаем второй запрос (логин)
        txt_token = await token_read()
        await websocket.send(json.dumps(await token_payload(txt_token)))
        second_response = await websocket.recv(); second_response = json.loads(second_response)
        if "error" in second_response["payload"]:
            print("Ошибка входа по токену, авторизуйтесь через СМС ", second_response["payload"])
            os.remove("token.txt")
            return "login_error"
        else:
            print(f"Успешный вход в аккаунт!\nИмя: {second_response["payload"]["profile"]["names"][0]["name"]}\nАйди: {second_response["payload"]["profile"]["id"]}\nНомер: {second_response["payload"]["profile"]["phone"]}")
            await websocket.send(json.dumps(shit_payload))
            message = await websocket.recv(); message = json.loads(message)
            if message["payload"] == None:
                message = await websocket.recv(); message = json.loads(message)
                await handle_message(message)

async def client_start():
    if os.path.exists("token.txt"):
        print(1)
        client = await token_login()
        if client == "login_error":
            print('login failed!')
            await sms_login()
    else:
        print(2)
        await sms_login()

asyncio.run(client_start())
