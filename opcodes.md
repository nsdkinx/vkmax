__Вход по токену__

*opcode: 19*

```{"ver":11,"cmd":0,"seq":1,"opcode":19,"payload":{"interactive":true,"token":"token","chatsSync":0,"contactsSync":0,"presenceSync":0,"draftsSync":0,"chatsCount":40}}```


__Получение списка контактов__

*opcode: 32*

```{"ver":11,"cmd":0,"seq":4,"opcode":32,"payload":{"contactIds":[id,id,id]}}```


__Добавление в контакты__

*opcode: 34*
```{"ver":11,"cmd":0,"seq":32,"opcode":34,"payload":{"contactId":id,"action":"ADD"}}```


__Получение текущего чата__

*opcode: 49*

```{"ver":11,"cmd":0,"seq":14,"opcode":49,"payload":{"chatId":chatid,"from":175xxxxxxxxxx,"forward":0,"backward":30,"getMessages":true}}```


__Отправка сообщения__

*opcode: 64*

```{"ver":11,"cmd":0,"seq":22,"opcode":64,"payload":{"chatId":chatid,"message":{"text":"message_text","cid":175xxxxxxxxxx,"elements":[],"attaches":[]},"notify":true}}```


__Отправка стикера__

*opcode: 64*

```{"ver":11,"cmd":0,"seq":122,"opcode":64,"payload":{"chatId":chatid,"message":{"cid":175xxxxxxxxxx,"attaches":[{"_type":"STICKER","stickerId":598965}]},"notify":true}}```


__Прочтение сообщения__

*opcode: 50*

```{"ver":11,"cmd":0,"seq":25,"opcode":50,"payload":{"type":"READ_MESSAGE","chatId":chatid,"messageId":messageid","mark":175xxxxxxxxxx}}```


__Реакция на сообщение__

*opcode: 178*

```{"ver":11,"cmd":0,"seq":13,"opcode":178,"payload":{"chatId":chatid,"messageId":"messageid","reaction":{"reactionType":"EMOJI","id":"❤️"}}}```


