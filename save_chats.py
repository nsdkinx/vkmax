#!/usr/bin/env python3
"""
Скрипт для сохранения сообщений чатов по дням.
Создает папку chats/{chat_id}/ и сохраняет файлы по дням.
При повторном запуске загружает только новые сообщения.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

from python_max_client.client import MaxClient
from python_max_client.functions.chats import get_chats, get_chat_messages
from python_max_client.functions.users import resolve_users

# Настройка логирования
logging.basicConfig(
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def get_chat_id_from_args():
    """Получить chat_id из аргументов командной строки"""
    if len(sys.argv) > 1:
        try:
            return int(sys.argv[1])
        except ValueError:
            logger.error("❌ Неверный формат chat_id. Используйте число.")
            sys.exit(1)
    return None


def load_existing_messages(chat_dir, date_str):
    """Загрузить существующие сообщения за день"""
    file_path = chat_dir / f"{date_str}.json"
    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"⚠️  Ошибка чтения файла {file_path}: {e}")
    return []


async def save_messages(client, chat_dir, date_str, messages):
    """Сохранить сообщения за день"""
    # Добавляем имена пользователей
    user_names = {}
    for msg in messages:
        sender_id = msg.get('sender')
        if sender_id and sender_id not in user_names:
            user_names[sender_id] = None  # Помечаем для получения имени
    
    # Получаем имена для всех отправителей
    if user_names:
        logger.info(f"👤 Получаем имена для {len(user_names)} пользователей...")
        names = await get_user_names(client, list(user_names.keys()))
        user_names.update(names)
    
    # Добавляем имена в сообщения
    for msg in messages:
        sender_id = msg.get('sender')
        if sender_id and sender_id in user_names:
            msg['sender_name'] = user_names[sender_id]
        else:
            msg['sender_name'] = f"User {sender_id}" if sender_id else "Unknown"
    
    file_path = chat_dir / f"{date_str}.json"
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 Сохранено {len(messages)} сообщений в {file_path}")
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения: {e}")


def get_last_message_id(messages):
    """Получить ID последнего сообщения"""
    if not messages:
        return None
    # Сортируем по времени и берем самое новое
    sorted_msgs = sorted(messages, key=lambda x: x.get('time', 0), reverse=True)
    return sorted_msgs[0].get('id') or sorted_msgs[0].get('messageId')


async def get_user_names(client, user_ids):
    """Получить имена пользователей по их ID"""
    if not user_ids:
        return {}
    
    try:
        response = await resolve_users(client, list(user_ids))
        if "payload" not in response or "contacts" not in response["payload"]:
            logger.warning(f"⚠️  Нет данных в ответе resolve_users для {user_ids}")
            return {}
            
        names = {}
        contacts = response["payload"]["contacts"]
        logger.info(f"👤 Получено контактов: {len(contacts)}")
        
        for contact in contacts:
            user_id = contact.get("id")
            if user_id:
                # Получаем имя из names массива
                contact_names = contact.get("names", [])
                if contact_names:
                    name = contact_names[0].get("name", f"User {user_id}")
                else:
                    name = f"User {user_id}"
                names[user_id] = name
                logger.info(f"👤 {user_id} -> {name}")
        return names
    except Exception as e:
        logger.warning(f"⚠️  Ошибка получения имен пользователей: {e}")
        return {}


def group_messages_by_date(messages):
    """Группировать сообщения по дням"""
    by_date = {}
    for msg in messages:
        msg_time = msg.get('time', 0)
        if msg_time:
            date = datetime.fromtimestamp(msg_time / 1000).strftime('%Y-%m-%d')
            if date not in by_date:
                by_date[date] = []
            by_date[date].append(msg)
    return by_date


async def load_new_messages(client, chat_id, from_message_id=None):
    """Загрузить новые сообщения с определенного ID"""
    all_messages = []
    seen_ids = set()
    last_msg_timestamp = from_message_id
    batch_count = 0
    user_names = {}  # Кэш имен пользователей
    
    try:
        while True:
            batch_count += 1
            
            # Загружаем порцию сообщений
            response = await get_chat_messages(
                client, chat_id, count=100, from_message_id=last_msg_timestamp
            )
            
            if "payload" not in response or "messages" not in response["payload"]:
                logger.warning("⚠️  Нет данных в ответе")
                break
                
            messages = response["payload"]["messages"]
            if not messages:
                logger.info("📭 Больше нет сообщений в чате")
                break
                
            # Фильтруем дубликаты и собираем ID пользователей
            new_messages = []
            user_ids_to_resolve = set()
            
            for msg in messages:
                msg_id = msg.get('id') or msg.get('messageId')
                if msg_id and msg_id not in seen_ids:
                    seen_ids.add(msg_id)
                    new_messages.append(msg)
                    
                    # Собираем ID отправителей для получения имен
                    sender_id = msg.get('sender')
                    if sender_id and sender_id not in user_names:
                        user_ids_to_resolve.add(sender_id)
                    
            if not new_messages:
                break
                
            # Получаем имена пользователей для новых отправителей
            if user_ids_to_resolve:
                logger.info(f"👤 Получаем имена для {len(user_ids_to_resolve)} пользователей: {list(user_ids_to_resolve)}")
                new_names = await get_user_names(client, list(user_ids_to_resolve))
                logger.info(f"👤 Получено имен: {len(new_names)}")
                user_names.update(new_names)
            
            # Добавляем имена в сообщения
            for msg in new_messages:
                sender_id = msg.get('sender')
                if sender_id and sender_id in user_names:
                    msg['sender_name'] = user_names[sender_id]
                else:
                    msg['sender_name'] = f"User {sender_id}" if sender_id else "Unknown"
                
            all_messages.extend(new_messages)
            logger.info(f"📥 Пакет {batch_count}: загружено {len(new_messages)} новых сообщений")
            
            # Получаем timestamp самого старого сообщения для следующей итерации
            # API возвращает messages от старых к новым, поэтому берем messages[0]
            last_message = messages[0]
            last_msg_timestamp = last_message.get("time", 0)
            
            if not last_msg_timestamp:
                logger.error("Не удалось получить timestamp последнего сообщения")
                break
                
            # Вычитаем 1 мс чтобы не получить то же сообщение снова
            last_msg_timestamp = last_msg_timestamp - 1
            
            if len(messages) < 100:  # Достигли конца
                logger.info("📭 Достигнут конец чата")
                break
                
            # Защита от бесконечного цикла
            if len(all_messages) > 10000:
                logger.warning("⚠️  Достигнут лимит в 10000 сообщений")
                break
                
            await asyncio.sleep(0.3)  # Пауза между запросами
            
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки сообщений: {e}")
        
    return all_messages


async def select_chat(client):
    """Выбрать чат из списка"""
    logger.info("📋 Получение списка чатов...")
    response = get_chats(client)
    
    if "payload" not in response or "chats" not in response["payload"]:
        logger.error("❌ Не удалось получить список чатов")
        return None
        
    chats = response["payload"]["chats"]
    
    # Фильтруем реальные чаты (убираем только служебные с restrictions=64)
    real_chats = []
    for chat in chats:
        chat_id = chat.get("id", 0)
        restrictions = chat.get("restrictions", 0)
        
        # Пропускаем только служебные чаты (restrictions=64) и избранное (id=0)
        if chat_id == 0 or restrictions == 64:
            continue
            
        real_chats.append(chat)
    
    if not real_chats:
        logger.warning("⚠️  Не найдено чатов")
        return None
        
    # Показываем список
    print("\n" + "=" * 50)
    print("💬 ВЫБЕРИТЕ ЧАТ:")
    print("=" * 50)
    
    for idx, chat in enumerate(real_chats, 1):
        chat_id = chat.get("id")
        chat_type = chat.get("type", "UNKNOWN")
        
        # Определяем название чата
        title = chat.get("title", "")
        if not title and "member" in chat:
            member = chat["member"]
            if "names" in member and member["names"]:
                title = member["names"][0].get("name", f"Chat {chat_id}")
            else:
                title = f"Chat {chat_id}"
        elif not title:
            title = f"Chat {chat_id}"
        
        # Иконка типа чата
        icon = {"DIALOG": "👤", "CHAT": "👥", "CHANNEL": "📢"}.get(chat_type, "💭")
        
        # Количество участников
        participants_count = chat.get("participantsCount", 0)
        participants_str = f" ({participants_count} участников)" if participants_count > 0 else ""
        
        # Непрочитанные сообщения
        unread = chat.get("newMessages", 0)
        unread_str = f" 🔴 {unread}" if unread > 0 else ""
        
        # Последнее сообщение (краткий превью)
        last_msg_preview = ""
        if "lastMessage" in chat:
            last_msg = chat["lastMessage"]
            text = last_msg.get("text", "")
            if text:
                preview = text[:30] + "..." if len(text) > 30 else text
                last_msg_preview = f" | {preview}"
        
        print(f"{idx}. {icon} {title}{participants_str}{unread_str}{last_msg_preview}")
        print(f"   ID: {chat_id} | Тип: {chat_type}")
    
    print("=" * 50)
    
    while True:
        try:
            choice = input(f"\nВыберите чат (1-{len(real_chats)}): ").strip()
            if not choice:
                return None
            idx = int(choice) - 1
            if 0 <= idx < len(real_chats):
                return real_chats[idx]
            else:
                print("❌ Неверный номер")
        except ValueError:
            print("❌ Введите число")


async def main():
    """Основная функция"""
    # Получаем chat_id из аргументов или выбираем интерактивно
    chat_id = get_chat_id_from_args()
    selected_chat = None
    
    client = MaxClient()
    
    try:
        # Подключение и авторизация
        logger.info("🔌 Подключение к VK MAX...")
        await client.connect()
        
        token_file = Path("login_token.txt")
        if not token_file.exists():
            logger.error("❌ Файл login_token.txt не найден!")
            return
            
        token = token_file.read_text(encoding="utf-8").strip()
        logger.info("🔑 Авторизация...")
        await client.login_by_token(token)
        logger.info("✅ Авторизация успешна!")
        
        # Выбираем чат
        if chat_id:
            # Ищем чат по ID
            response = get_chats(client)
            if "payload" in response and "chats" in response["payload"]:
                for chat in response["payload"]["chats"]:
                    if chat.get("id") == chat_id:
                        selected_chat = chat
                        break
                if not selected_chat:
                    logger.error(f"❌ Чат с ID {chat_id} не найден")
                    return
        else:
            selected_chat = await select_chat(client)
            if not selected_chat:
                return
                
        chat_id = selected_chat.get("id")
        
        # Определяем название чата (та же логика, что и в select_chat)
        chat_title = selected_chat.get("title", "")
        if not chat_title and "member" in selected_chat:
            member = selected_chat["member"]
            if "names" in member and member["names"]:
                chat_title = member["names"][0].get("name", f"Chat {chat_id}")
            else:
                chat_title = f"Chat {chat_id}"
        elif not chat_title:
            chat_title = f"Chat {chat_id}"
        
        # Дополнительная информация о чате
        chat_type = selected_chat.get("type", "UNKNOWN")
        participants_count = selected_chat.get("participantsCount", 0)
        participants_str = f" ({participants_count} участников)" if participants_count > 0 else ""
        
        logger.info(f"📱 Выбран чат: {chat_title}{participants_str} (ID: {chat_id}, тип: {chat_type})")
        
        # Создаем папку для чата
        chats_dir = Path("chats")
        chat_dir = chats_dir / str(chat_id)
        chat_dir.mkdir(parents=True, exist_ok=True)
        
        # Определяем период (последние 7 дней)
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        
        logger.info(f"📅 Загружаем сообщения с {week_ago.strftime('%d.%m.%Y')} по {now.strftime('%d.%m.%Y')}")
        
        # Загружаем все сообщения за период
        all_messages = []
        seen_ids = set()
        last_msg_id = None
        
        # Проверяем, есть ли уже сохраненные сообщения
        existing_dates = set()
        for date_file in chat_dir.glob("*.json"):
            date_str = date_file.stem
            existing_dates.add(date_str)
            existing_msgs = load_existing_messages(chat_dir, date_str)
            for msg in existing_msgs:
                msg_id = msg.get('id') or msg.get('messageId')
                if msg_id:
                    seen_ids.add(msg_id)
        
        if existing_dates:
            logger.info(f"📁 Найдены существующие данные за {len(existing_dates)} дней")
            # Находим самый новый timestamp из существующих данных
            for date_str in existing_dates:
                existing_msgs = load_existing_messages(chat_dir, date_str)
                if existing_msgs:
                    # Сортируем по времени и берем самое новое
                    sorted_msgs = sorted(existing_msgs, key=lambda x: x.get('time', 0), reverse=True)
                    if sorted_msgs:
                        latest_timestamp = sorted_msgs[0].get('time', 0)
                        if latest_timestamp and (not last_msg_id or latest_timestamp > last_msg_id):
                            last_msg_id = latest_timestamp
        
        # Загружаем новые сообщения
        if last_msg_id:
            logger.info(f"🔄 Загружаем новые сообщения с ID {last_msg_id}")
        else:
            logger.info("🔄 Загружаем все сообщения за период")
            
        new_messages = await load_new_messages(client, chat_id, last_msg_id)
        
        if not new_messages:
            logger.info("✅ Новых сообщений не найдено")
            return
            
        # Группируем по дням и сохраняем
        by_date = group_messages_by_date(new_messages)
        
        for date_str, messages in by_date.items():
            # Загружаем существующие сообщения за этот день
            existing_msgs = load_existing_messages(chat_dir, date_str)
            
            # Объединяем и убираем дубликаты
            all_day_msgs = existing_msgs + messages
            unique_msgs = []
            seen_day_ids = set()
            
            for msg in all_day_msgs:
                msg_id = msg.get('id') or msg.get('messageId')
                if msg_id and msg_id not in seen_day_ids:
                    seen_day_ids.add(msg_id)
                    unique_msgs.append(msg)
            
            # Сортируем по времени
            unique_msgs.sort(key=lambda x: x.get('time', 0))
            
            # Сохраняем
            await save_messages(client, chat_dir, date_str, unique_msgs)
        
        logger.info(f"✅ Обработано {len(new_messages)} новых сообщений")
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}", exc_info=True)
    finally:
        await client.disconnect()
        logger.info("👋 Отключено от сервера")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Прервано пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)
