"""
Анализ чатов с помощью GigaChat
Переиспользование кода из analyze_chat.py
"""
import json
import logging
import base64
import re
from datetime import datetime
from typing import List, Dict, Optional
import requests
import urllib3

# Отключаем предупреждения о SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class ChatAnalyzer:
    """Класс для анализа чатов с помощью GigaChat"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def decode_api_key(self, encoded_key: str) -> str:
        """Декодировать API ключ из base64"""
        try:
            return base64.b64decode(encoded_key).decode('utf-8')
        except Exception as e:
            logger.warning(f"⚠️  Не удалось декодировать API ключ: {e}")
            return encoded_key
    
    def optimize_text(self, messages: List[Dict]) -> List[Dict]:
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
            time = msg.get('message_time', 0)
            
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
    
    def format_chat_for_analysis(self, messages: List[Dict]) -> str:
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
    
    def get_gigachat_token(self) -> Optional[str]:
        """Получить access token для GigaChat"""
        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        
        # Декодируем API ключ если нужно
        api_key = self.api_key
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
    
    def call_gigachat_api(self, text: str) -> Optional[str]:
        """Вызвать GigaChat API для суммаризации"""
        # Сначала получаем access token
        access_token = self.get_gigachat_token()
        if not access_token:
            return None
        
        url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        prompt = f"""Действуй так как будто ты учитель первого класса и это твой родительский чат, тебя зовут Виктория Романовна. Проанализируй сообщения родительского чат, в чате 45 человек. Включи ТОЛЬКО важные события, которые требуют действий от родителей. Сейчас уже конец дня и нужно сообщить всем родителям общую информацию о том что сегодня было за день, что надо сделать завта и что надо сделать в ближайшем будущем.

ИГНОРИРУЙ микроменеджмент и перемещения:
- Кто кого забирает/отпускает, надо отпустить, ждет, идет, кто приехал, кто уехал
- Кто где ждет (у школы, дома, на остановке), информацию по перемещениям людей, детей и родителей
- Координацию встреч и перемещений
- Уточнения без последствий, Бытовые вопросы
- Пустые сообщения "Я тоже", "кто идет", "забираю" 


ВАЖНО: Если есть ссылки на что-то, что нужно сделать - ОБЯЗАТЕЛЬНО выводи их!

Чат:
{text}

Формат резюме:

## 📋 НОВАЯ ИНФОРМАЦИЯ(если есть):
- Что за нововведения, или напоминания, Точные требования, Штрафы/последствия, ссылки на регламенты/положения (если есть)

## 🚨 Родителям(если есть):
- Что именно сделать (конкретно), К какому сроку, Ссылки на документы/формы/сайты (если есть)

## ⚠️ Детям(если есть):
- Что именно сделать (конкретно), К какому сроку, Ссылки на документы/формы/сайты (если есть)

ВАЖНО! Пиши только про то что было в сообщениях, Дополнительно ничего не пиши.
Если нет проблем,нововведений, мероприятий, требований действий, новых правил, ссылок то не пиши про них. Если нет событий, то не пиши про них. 
Пиши как будто ты отлично знаешь и руководствуешься книжкой "Пиши Сокращай".
Только факты. Только действия. Без воды."""

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
    
    def analyze_chat_by_date(self, messages: List[Dict]) -> Optional[str]:
        """Анализировать чат за определенную дату"""
        try:
            # Оптимизируем текст
            logger.info("🔧 Оптимизируем текст...")
            optimized_messages = self.optimize_text(messages)
            
            # Форматируем для анализа
            formatted_text = self.format_chat_for_analysis(optimized_messages)
            
            logger.info(f"📊 Статистика:")
            logger.info(f"   Всего сообщений: {len(messages)}")
            logger.info(f"   После оптимизации: {len(optimized_messages)}")
            logger.info(f"   Длина текста: {len(formatted_text)} символов")
            
            # Вызываем GigaChat
            logger.info("🤖 Отправляем запрос в GigaChat...")
            summary = self.call_gigachat_api(formatted_text)
            
            if summary:
                logger.info("✅ Суммаризация получена")
                return summary
            else:
                logger.error("❌ Не удалось получить резюме от GigaChat")
                return None
                
        except Exception as e:
            logger.error(f"❌ Ошибка анализа чата: {e}")
            return None
