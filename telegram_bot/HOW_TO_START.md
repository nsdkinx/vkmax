# 🚀 КАК ЗАПУСТИТЬ БОТА С РЕАЛЬНЫМИ ТОКЕНАМИ

## 📋 Шаги для запуска

### 1. Установите переменные окружения

```bash
# Telegram Bot Token (получите у @BotFather)
export TELEGRAM_BOT_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"

# GigaChat API Key (получите на https://developers.sber.ru/portal/products/gigachat)
export GIGACHAT_API_KEY="your_gigachat_api_key_here"

# VK MAX Token (у вас уже есть)
export VK_MAX_TOKEN="An_Sx6HQ9HDiF9vtpuinKmOWnCKmvmV3F9AAo_7iENVJVRhvszK_pE3QjcHRzSWTCHsDivbZNYmTrj5_Yfe0K922s-D_YxYGvicGgKV5HDLxcB4ZYxNaxkAPOALicRDDMJ3ZKEAox3HcXTlaInxpJ-qOVeolrIIvHYKkeHKAt6Iix3a4gk_6warHNGFkRcXePYT1n1QzwYYZNvUpGGnmYTA9Kk97K1aBpnRoMd5ulLO53nT19NC0T6egmRBUTjpsCiHcFqzKbygCO6LULw3LPPHiUd51cDyiGYfrCyCDaY8dXga7A0FPykf6EIwfwtvO7IvoXHihDY7FHw7rKO75e3xHhDrorBopSK8IG1geew-UoKY3TNw5xtV5jJf6Gut91YNA-YuqEWyFE76wVOIWfWmGni7cd4F6w7KEeY1Hg2VATV1d105x1QJXqsoV86B1APG-GhAzMwA2QGNpxT3ETqHezs9SYj5q0FZ6uh2TsOf_y0xo9hMM774MCuwzr4jAH_x0l8CAEO9_0QEWJHw9Z8uC6FZxRUpI0PMmfDW19yTJ4p6OQDsD0NwoVIP7EcSs1k_AbiasnHgQwkrqoZMPIbc2Y9yZcIHCiAL56hSENaXPg0Y0YUYNnegi9k2O6QHq0n9P84kBLQA9YO40s5811OnD3sQu9j0rGMKgI2_BYt6umN0DKzUGq3e49zr_dXXOZpEG57Y"
```

### 2. Запустите бота

```bash
# Способ 1: Через специальный скрипт
python start_with_tokens.py

# Способ 2: Через основной скрипт
python run_bot.py
```

## 🔧 Получение токенов

### Telegram Bot Token
1. Напишите @BotFather в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Получите токен вида `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

### GigaChat API Key
1. Зайдите на https://developers.sber.ru/portal/products/gigachat
2. Зарегистрируйтесь и получите API ключ
3. Используйте ключ для переменной `GIGACHAT_API_KEY`

### VK MAX Token
✅ У вас уже есть токен в `login_token.txt`

## 🧪 Тестирование

### Проверка токенов
```bash
# Проверьте, что токены установлены
echo "TELEGRAM_BOT_TOKEN: $TELEGRAM_BOT_TOKEN"
echo "GIGACHAT_API_KEY: $GIGACHAT_API_KEY" 
echo "VK_MAX_TOKEN: $VK_MAX_TOKEN"
```

### Демонстрационный режим
```bash
# Запустите демо без реальных токенов
python demo_mode.py
```

## 🚀 Готово!

После установки токенов бот будет:
- ✅ Подключаться к Telegram API
- ✅ Работать с VK MAX
- ✅ Анализировать чаты через GigaChat
- ✅ Сохранять данные в SQLite
- ✅ Публиковать результаты в группы

**Удачного использования!** 🎉
