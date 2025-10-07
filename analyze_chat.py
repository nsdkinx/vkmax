#!/usr/bin/env python3
"""
Скрипт для анализа чатов с помощью GigaChat
Позволяет выбрать день из сохраненных файлов чатов и получить краткое резюме
"""

import json
import logging
import os
import sys
from pathlib import Path
from datetime import datetime
import requests
import re
import urllib3
import base64

# Отключаем предупреждения о SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Загружаем переменные из .env файла
def load_env():
    """Загрузить переменные из .env файла"""
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# Загружаем переменные окружения
load_env()

def decode_api_key(encoded_key):
    """Декодировать API ключ из base64"""
    try:
        return base64.b64decode(encoded_key).decode('utf-8')
    except Exception as e:
        logger.warning(f"⚠️  Не удалось декодировать API ключ: {e}")
        return encoded_key

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_available_chats():
    """Получить список доступных чатов"""
    chats_dir = Path("chats")
    if not chats_dir.exists():
        logger.error("❌ Папка 'chats' не найдена")
        return []
    
    chats = []
    for chat_dir in chats_dir.iterdir():
        if chat_dir.is_dir():
            chat_id = chat_dir.name
            # Подсчитываем количество файлов в чате
            json_files = list(chat_dir.glob("*.json"))
            if json_files:
                # Получаем даты файлов
                dates = [f.stem for f in json_files]
                dates.sort()
                chats.append({
                    'id': chat_id,
                    'dates': dates,
                    'files_count': len(json_files)
                })
    
    return sorted(chats, key=lambda x: x['files_count'], reverse=True)

def select_chat():
    """Выбрать чат для анализа"""
    chats = get_available_chats()
    
    if not chats:
        logger.error("❌ Не найдено чатов для анализа")
        return None
    
    print("📱 Доступные чаты:")
    for idx, chat in enumerate(chats, 1):
        print(f"{idx}. Чат {chat['id']} ({chat['files_count']} дней)")
        print(f"   Даты: {chat['dates'][0]} - {chat['dates'][-1]}")
    
    try:
        choice = int(input("\nВыберите номер чата: ")) - 1
        if 0 <= choice < len(chats):
            return chats[choice]
        else:
            logger.error("❌ Неверный номер чата")
            return None
    except ValueError:
        logger.error("❌ Введите корректный номер")
        return None

def select_date(chat):
    """Выбрать дату для анализа"""
    print(f"\n📅 Доступные даты для чата {chat['id']}:")
    
    # Показываем последние 10 дат с количеством сообщений
    recent_dates = chat['dates'][-10:]
    for idx, date in enumerate(recent_dates, 1):
        # Подсчитываем количество сообщений для этой даты
        file_path = Path("chats") / chat['id'] / f"{date}.json"
        message_count = 0
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    messages = json.load(f)
                    message_count = len(messages)
            except:
                message_count = 0
        
        print(f"{idx}. {date} ({message_count} сообщений)")
    
    try:
        choice = int(input("\nВыберите номер даты: ")) - 1
        if 0 <= choice < len(recent_dates):
            selected_date = recent_dates[choice]
            logger.info(f"📅 Выбрана дата: {selected_date}")
            return selected_date
        else:
            logger.error("❌ Неверный номер даты")
            return None
    except ValueError:
        logger.error("❌ Введите корректный номер")
        return None

def load_chat_messages(chat_id, date):
    """Загрузить сообщения из файла"""
    file_path = Path("chats") / chat_id / f"{date}.json"
    
    if not file_path.exists():
        logger.error(f"❌ Файл {file_path} не найден")
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            messages = json.load(f)
        logger.info(f"📥 Загружено {len(messages)} сообщений из {file_path}")
        return messages
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки файла: {e}")
        return []

def optimize_text(messages):
    """Оптимизировать текст чата для передачи в языковую модель"""
    optimized_messages = []
    
    for msg in messages:
        text = msg.get('text', '').strip()
        if not text:
            continue
            
        # Убираем лишние символы и сокращаем
        text = re.sub(r'\s+', ' ', text)  # Убираем лишние пробелы
        text = re.sub(r'[^\w\s\.,!?\-:;()]', '', text)  # Убираем спецсимволы
        
        # Сокращаем очень длинные сообщения
        if len(text) > 200:
            text = text[:200] + "..."
        
        sender_name = msg.get('sender_name', 'Неизвестно')
        time = msg.get('time', 0)
        
        # Форматируем время
        if time:
            dt = datetime.fromtimestamp(time / 1000)
            time_str = dt.strftime('%H:%M')
        else:
            time_str = "??:??"
        
        optimized_messages.append({
            'time': time_str,
            'sender': sender_name,
            'text': text
        })
    
    return optimized_messages

def format_chat_for_analysis(messages):
    """Форматировать чат для анализа"""
    if not messages:
        return ""
    
    # Группируем по времени для лучшего понимания контекста
    formatted_lines = []
    
    for msg in messages:
        time_str = msg['time']
        sender = msg['sender']
        text = msg['text']
        
        # Форматируем строку сообщения
        line = f"[{time_str}] {sender}: {text}"
        formatted_lines.append(line)
    
    # Объединяем все сообщения
    full_text = "\n".join(formatted_lines)
    
    # Ограничиваем длину текста для экономии токенов
    max_length = 8000  # Примерно 2000 токенов
    if len(full_text) > max_length:
        full_text = full_text[:max_length] + "\n... (текст обрезан для экономии токенов)"
    
    return full_text

def get_gigachat_token(api_key):
    """Получить access token для GigaChat"""
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    
    # Декодируем API ключ если нужно
    if len(api_key) > 50:  # Если это base64
        try:
            api_key = base64.b64decode(api_key).decode('utf-8')
        except:
            pass
    
    # Кодируем ключ для Basic Auth
    auth_string = base64.b64encode(api_key.encode()).decode()
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': '747035d0-e55d-4b35-82cb-a882800f7121',
        'Authorization': f'Basic {auth_string}'
    }
    
    payload = {
        'scope': 'GIGACHAT_API_PERS'
    }
    
    try:
        logger.info("🔑 Получаем access token...")
        response = requests.post(url, headers=headers, data=payload, timeout=30, verify=False)
        
        if response.status_code == 200:
            result = response.json()
            if 'access_token' in result:
                logger.info("✅ Access token получен")
                return result['access_token']
            else:
                logger.error(f"❌ Нет access_token в ответе: {result}")
                return None
        else:
            logger.error(f"❌ Ошибка получения token: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Ошибка запроса token: {e}")
        return None

def call_gigachat_api(text, api_key):
    """Вызвать GigaChat API для суммаризации"""
    # Сначала получаем access token
    access_token = get_gigachat_token(api_key)
    if not access_token:
        return None
    
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    prompt = f"""Проанализируй следующий родительский чат и создай краткое резюме для родителя. 

ВАЖНО: Игнорируй спам-сообщения типа "отпускаю ребенка", "забираю", "кто идет", "я тоже" и подобные. Фокусируйся только на значимой информации.

Чат:
{text}

Создай структурированное резюме в следующем формате:

## 🎯 Основные события и новости:
- Важные объявления и изменения
- Новые правила или требования
- Предстоящие мероприятия

## ⚠️ Проблемы, требующие внимания:
- Вопросы, которые нужно решить
- Проблемы с организацией
- Требования к родителям

## ✅ Решения и ответы:
- Как решаются проблемы
- Что нужно сделать родителям
- Важные сроки и даты

## 📋 Что нужно знать родителю:
- Ключевые изменения в расписании
- Требования к детям (форма, принадлежности)
- Важные контакты или информация

## 🚫 Игнорировать:
- Сообщения о том, кто кого забирает/отпускает
- Повторяющиеся бытовые вопросы
- Несущественные детали

Будь кратким, ясным и фокусируйся только на важной информации для родителей."""

    data = {
        "model": "GigaChat:latest",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        logger.info(f"🔗 Отправляем запрос на {url}")
        logger.info(f"📝 Длина текста: {len(text)} символов")
        
        # Используем json параметр с правильной кодировкой
        response = requests.post(url, headers=headers, json=data, timeout=30, verify=False)
        logger.info(f"📡 Получен ответ: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"📋 Структура ответа: {list(result.keys())}")
            
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                logger.error("❌ Неожиданный формат ответа от GigaChat")
                logger.error(f"📋 Полный ответ: {result}")
                return None
        else:
            logger.error(f"❌ HTTP ошибка: {response.status_code}")
            logger.error(f"📋 Ответ сервера: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Ошибка запроса к GigaChat: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка: {e}")
        return None

def main():
    """Основная функция"""
    print("🤖 Анализатор чатов с GigaChat")
    print("=" * 50)
    
    # Проверяем наличие API ключа
    api_key = os.getenv('GIGACHAT_API_KEY')
    if not api_key:
        print("❌ Не найден API ключ GigaChat")
        print("Установите переменную окружения GIGACHAT_API_KEY")
        print("\n🔧 Режим тестирования (без API):")
        api_key = "test_key"  # Для тестирования
    else:
        print(f"✅ API ключ найден: {api_key[:10]}...")
        # Декодируем API ключ из base64
        api_key = decode_api_key(api_key)
        print(f"🔑 Декодированный ключ: {api_key[:20]}...")
    
    # Выбираем чат
    chat = select_chat()
    if not chat:
        return
    
    # Выбираем дату
    date = select_date(chat)
    if not date:
        return
    
    # Загружаем сообщения
    messages = load_chat_messages(chat['id'], date)
    if not messages:
        return
    
    # Оптимизируем текст
    logger.info("🔧 Оптимизируем текст...")
    optimized_messages = optimize_text(messages)
    
    # Форматируем для анализа
    formatted_text = format_chat_for_analysis(optimized_messages)
    
    print(f"\n📊 Статистика:")
    print(f"   Всего сообщений: {len(messages)}")
    print(f"   После оптимизации: {len(optimized_messages)}")
    print(f"   Длина текста: {len(formatted_text)} символов")
    
    # Вызываем GigaChat
    if api_key == "test_key":
        print(f"\n🤖 Тестовый режим - показываем оптимизированный текст:")
        print("=" * 50)
        print(formatted_text[:500] + "..." if len(formatted_text) > 500 else formatted_text)
        print("=" * 50)
        print("\n📋 В реальном режиме здесь было бы резюме от GigaChat")
        return
    
    print(f"\n🤖 Отправляем запрос в GigaChat...")
    summary = call_gigachat_api(formatted_text, api_key)
    
    if summary:
        print(f"\n📋 Резюме чата за {date}:")
        print("=" * 50)
        print(summary)
        print("=" * 50)
        
        # Сохраняем результат
        output_file = Path("chats") / chat['id'] / f"{date}_summary.txt"
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Резюме чата за {date}\n")
                f.write("=" * 50 + "\n")
                f.write(summary)
            logger.info(f"💾 Резюме сохранено в {output_file}")
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения: {e}")
    else:
        print("❌ Не удалось получить резюме от GigaChat")

if __name__ == "__main__":
    main()
