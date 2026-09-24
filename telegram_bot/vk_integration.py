"""
Интеграция с VK MAX API
Переиспользование кода из save_chats.py и analyze_chat.py
"""
import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

from python_max_client.client import MaxClient
from python_max_client.functions.chats import get_chats, get_chat_messages
from python_max_client.functions.users import resolve_users

logger = logging.getLogger(__name__)

class VKMaxIntegration:
    """Класс для интеграции с VK MAX API"""
    
    def __init__(self, token: str):
        self.token = token
        self.client = None
    
    async def connect(self):
        """Подключиться к VK MAX"""
        try:
            self.client = MaxClient()
            await self.client.connect()
            await self.client.login_by_token(self.token)
            logger.info("✅ Подключение к VK MAX успешно")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к VK MAX: {e}")
            return False
    
    async def disconnect(self):
        """Отключиться от VK MAX"""
        if self.client:
            await self.client.disconnect()
            self.client = None
    
    async def get_chat_info(self, chat_id: str) -> Optional[Dict]:
        """Получить информацию о чате"""
        if not self.client:
            return None
        
        try:
            response = get_chats(self.client)
            if "payload" not in response or "chats" not in response["payload"]:
                return None
            
            chats = response["payload"]["chats"]
            for chat in chats:
                if str(chat.get("id")) == str(chat_id):
                    return {
                        "id": chat.get("id"),
                        "title": chat.get("title", ""),
                        "type": chat.get("type", "UNKNOWN"),
                        "participants_count": chat.get("participantsCount", 0)
                    }
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка получения информации о чате: {e}")
            return None
    
    async def check_chat_access(self, chat_id: str) -> bool:
        """Проверить доступ к чату"""
        chat_info = await self.get_chat_info(chat_id)
        return chat_info is not None
    
    async def get_available_chats(self) -> List[Dict]:
        """Получить список всех доступных чатов"""
        if not self.client:
            return []
        
        try:
            response = get_chats(self.client)
            if "payload" not in response or "chats" not in response["payload"]:
                return []
            
            chats = response["payload"]["chats"]
            formatted_chats = []
            
            for chat in chats:
                formatted_chats.append({
                    "id": str(chat.get("id", "")),
                    "title": chat.get("title", "Без названия"),
                    "type": chat.get("type", "UNKNOWN"),
                    "participants_count": chat.get("participantsCount", 0),
                    "description": chat.get("description", "")
                })
            
            # Сортируем по количеству участников (убывание)
            formatted_chats.sort(key=lambda x: x["participants_count"], reverse=True)
            
            logger.info(f"✅ Получено {len(formatted_chats)} доступных чатов")
            return formatted_chats
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка чатов: {e}")
            return []
    
    async def load_chat_messages(self, chat_id: str, days_back: int = 7, db_manager=None, load_only_new: bool = False) -> List[Dict]:
        """Загрузить сообщения чата за последние дни (по образцу save_chats.py)"""
        if not self.client:
            return []
        
        try:
            all_messages = []
            seen_ids = set()
            
            # Определяем начальную точку загрузки
            if load_only_new and db_manager:
                # Загружаем только новые сообщения после последнего сохраненного
                last_timestamp = db_manager.get_last_message_timestamp(chat_id)
                if last_timestamp:
                    # Для загрузки новых сообщений начинаем с текущего времени
                    # и идем назад до последнего сохраненного сообщения
                    last_msg_timestamp = int(datetime.now().timestamp() * 1000)
                    logger.info(f"📥 Загружаем только новые сообщения чата {chat_id} после {last_timestamp}...")
                else:
                    last_msg_timestamp = int(datetime.now().timestamp() * 1000)
                    logger.info(f"📥 Первая загрузка сообщений чата {chat_id}...")
            else:
                # Загружаем все сообщения за указанный период
                last_msg_timestamp = int(datetime.now().timestamp() * 1000)
                logger.info(f"📥 Загружаем сообщения чата {chat_id} за последние {days_back} дней...")
            
            batch_count = 0
            user_names = {}  # Кэш имен пользователей
            
            while True:
                try:
                    batch_count += 1
                    
                    # Загружаем порцию сообщений
                    response = await get_chat_messages(
                        self.client, 
                        int(chat_id), 
                        count=100, 
                        from_message_id=last_msg_timestamp
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
                        logger.info(f"👤 Получаем имена для {len(user_ids_to_resolve)} пользователей")
                        new_names = await self._get_user_names(list(user_ids_to_resolve))
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
                    
                    # Проверяем, достигли ли мы последнего сохраненного сообщения (для загрузки новых)
                    if load_only_new and db_manager and last_timestamp:
                        # Проверяем, есть ли в загруженных сообщениях те, которые уже есть в БД
                        found_old_message = False
                        for msg in new_messages:
                            msg_time = msg.get("time", 0)
                            if msg_time <= last_timestamp:
                                found_old_message = True
                                logger.info(f"📭 Достигнуто последнее сохраненное сообщение (timestamp: {last_timestamp})")
                                break
                        
                        if found_old_message:
                            # Фильтруем только новые сообщения (после last_timestamp)
                            filtered_messages = []
                            for msg in all_messages:
                                msg_time = msg.get("time", 0)
                                if msg_time > last_timestamp:
                                    filtered_messages.append(msg)
                            all_messages = filtered_messages
                            logger.info(f"📥 Отфильтровано до {len(all_messages)} новых сообщений")
                            break
                    
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
                    break
            
            logger.info(f"✅ Загружено {len(all_messages)} сообщений")
            return all_messages
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки сообщений чата: {e}")
            return []
    
    async def _get_user_names(self, user_ids: List[int]) -> Dict[int, str]:
        """Получить имена пользователей по их ID (по образцу save_chats.py)"""
        if not user_ids:
            return {}
        
        try:
            response = await resolve_users(self.client, list(user_ids))
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
    
    def format_messages_for_db(self, messages: List[Dict], chat_id: str) -> List[Dict]:
        """Форматировать сообщения для сохранения в БД (по образцу save_chats.py)"""
        formatted_messages = []
        
        for msg in messages:
            # Извлекаем основную информацию (структура из VK MAX API)
            message_id = msg.get("id", "") or msg.get("messageId", "")
            sender_id = msg.get("sender")
            text = msg.get("text", "")
            message_time = msg.get("time", 0)
            
            # Форматируем время
            if message_time:
                dt = datetime.fromtimestamp(message_time / 1000)
                date_str = dt.strftime("%Y-%m-%d")
            else:
                date_str = datetime.now().strftime("%Y-%m-%d")
            
            # Получаем имя отправителя (уже добавлено в load_chat_messages)
            sender_name = msg.get("sender_name", f"User {sender_id}" if sender_id else "Unknown")
            
            # Обрабатываем вложения
            attachments = []
            if "attachments" in msg:
                for attachment in msg["attachments"]:
                    att_type = attachment.get("type", "unknown")
                    attachments.append({
                        "type": att_type,
                        "data": attachment.get("data", {})
                    })
            
            # Обрабатываем реакции
            reaction_info = {}
            if "reactions" in msg:
                reaction_info = msg["reactions"]
            
            # Обрабатываем элементы сообщения (если есть)
            elements = []
            if "elements" in msg:
                elements = msg["elements"]
            
            formatted_msg = {
                "message_id": message_id,
                "sender_id": sender_id,
                "sender_name": sender_name,
                "text": text,
                "message_time": message_time,
                "date": date_str,
                "message_type": "USER",
                "attachments": attachments,
                "reaction_info": reaction_info,
                "elements": elements
            }
            
            formatted_messages.append(formatted_msg)
        
        return formatted_messages
    
    async def save_messages_to_db(self, db_manager, chat_id: str, messages: List[Dict]):
        """Сохранить сообщения в базу данных"""
        try:
            formatted_messages = self.format_messages_for_db(messages, chat_id)
            db_manager.save_messages(chat_id, formatted_messages)
            logger.info(f"✅ Сохранено {len(formatted_messages)} сообщений в БД")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения в БД: {e}")
            return False
