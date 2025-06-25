*Вход по токену*

__opcode: 19__
```{"ver":11,"cmd":0,"seq":1,"opcode":19,"payload":{"interactive":true,"token":"token","chatsSync":0,"contactsSync":0,"presenceSync":0,"draftsSync":0,"chatsCount":40}}```


*Получение списка контактов*

__opcode: 32__
```{"ver":11,"cmd":0,"seq":4,"opcode":32,"payload":{"contactIds":[id,id,id]}}```


*Получение текущего чата*

__opcode: 49__
```{"ver":11,"cmd":0,"seq":14,"opcode":49,"payload":{"chatId":chatid,"from":175xxxxxxxxxx,"forward":0,"backward":30,"getMessages":true}}```


*Отправка сообщения*

__opcode: 64__
```{"ver":11,"cmd":0,"seq":22,"opcode":64,"payload":{"chatId":chatid,"message":{"text":"message_text","cid":175xxxxxxxxxx,"elements":[],"attaches":[]},"notify":true}}```


*Отправка стикера*

__opcode: 64__
```{"ver":11,"cmd":0,"seq":122,"opcode":64,"payload":{"chatId":chatid,"message":{"cid":175xxxxxxxxxx,"attaches":[{"_type":"STICKER","stickerId":598965}]},"notify":true}}```


*Прочтение сообщения*

__opcode: 50__
```{"ver":11,"cmd":0,"seq":25,"opcode":50,"payload":{"type":"READ_MESSAGE","chatId":chatid,"messageId":messageid","mark":175xxxxxxxxxx}}```


*Реакция на сообщение*

__opcode: 178__
```{"ver":11,"cmd":0,"seq":13,"opcode":178,"payload":{"chatId":chatid,"messageId":"messageid","reaction":{"reactionType":"EMOJI","id":"❤️"}}}```


