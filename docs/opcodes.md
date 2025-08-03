## Вход по токену

*opcode: 19*

```{"ver":11,"cmd":0,"seq":1,"opcode":19,"payload":{"interactive":true,"token":"token","chatsSync":0,"contactsSync":0,"presenceSync":0,"draftsSync":0,"chatsCount":40}}```


## Получение списка контактов

*opcode: 32*

```{"ver":11,"cmd":0,"seq":4,"opcode":32,"payload":{"contactIds":[id,id,id]}}```


## Добавление в контакты / взаимодействие с пользователем

*opcode: 34*
```{"ver":11,"cmd":0,"seq":32,"opcode":34,"payload":{"contactId":id,"action":"ADD"}}```


## Получение текущего чата

*opcode: 49*

```{"ver":11,"cmd":0,"seq":14,"opcode":49,"payload":{"chatId":chatid,"from":175xxxxxxxxxx,"forward":0,"backward":30,"getMessages":true}}```


## Взаимодействие с пользователями в чате

*opcode: 77*

```{"ver":11,"cmd":0,"seq":36,"opcode":77,"payload":{"chatId":chatid,"userIds":[id,id],"showHistory":true,"operation":"add"}}```


## Отправка сообщения

*opcode: 64*

```{"ver":11,"cmd":0,"seq":22,"opcode":64,"payload":{"chatId":chatid,"message":{"text":"message_text","cid":175xxxxxxxxxx,"elements":[],"attaches":[]},"notify":true}}```


## Отправка стикера

*opcode: 64*

```{"ver":11,"cmd":0,"seq":122,"opcode":64,"payload":{"chatId":chatid,"message":{"cid":175xxxxxxxxxx,"attaches":[{"_type":"STICKER","stickerId":598965}]},"notify":true}}```


## Прочтение сообщения

*opcode: 50*

```{"ver":11,"cmd":0,"seq":25,"opcode":50,"payload":{"type":"READ_MESSAGE","chatId":chatid,"messageId":"messageid","mark":175xxxxxxxxxx}}```


## Редактирование сообщения

*opcode: 67*

```{"ver":11,"cmd":0,"seq":40,"opcode":67,"payload":{"chatId":chatid,"messageId":"messageid","text":"new_text","elements":[],"attachments":[]}}```


## Удаление сообщения

*opcode: 66*

```{'ver': 11, 'cmd': 0, 'seq': 4, 'opcode': 66, 'payload': {'chatId': chatid, 'messageIds': ['messageid'], 'forMe': False}}```


## Реакция на сообщение

*opcode: 178*

```{"ver":11,"cmd":0,"seq":13,"opcode":178,"payload":{"chatId":chatid,"messageId":"messageid","reaction":{"reactionType":"EMOJI","id":"❤️"}}}```


## Настройка профиля

*opcode: 22*

```{"ver":11,"cmd":0,"seq":24,"opcode":22,"payload":{"settings":{"user":{"HIDDEN":true}}}}```


