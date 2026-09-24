"""
Модуль для работы с SQLite базой данных
"""
import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Менеджер базы данных для Telegram бота"""
    
    def __init__(self, db_path: str = "bot_database.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Получить соединение с базой данных"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Инициализация базы данных - создание всех таблиц"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Пользователи бота
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Telegram группы
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS groups (
                    group_id INTEGER PRIMARY KEY,
                    group_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Связь пользователей с группами
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS group_users (
                    group_id INTEGER,
                    user_id INTEGER,
                    is_admin BOOLEAN DEFAULT FALSE,
                    PRIMARY KEY (group_id, user_id)
                )
            """)
            
            # Чаты VK MAX
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vk_chats (
                    chat_id TEXT PRIMARY KEY,
                    chat_name TEXT,
                    chat_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Связь групп с чатами VK MAX
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS group_vk_chats (
                    group_id INTEGER,
                    vk_chat_id TEXT,
                    added_by INTEGER,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (group_id, vk_chat_id)
                )
            """)
            
            # Сообщения по дням
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vk_chat_id TEXT NOT NULL,
                    message_id TEXT NOT NULL,
                    sender_id INTEGER,
                    sender_name TEXT,
                    text TEXT,
                    message_time INTEGER,
                    date TEXT,
                    message_type TEXT,
                    attachments TEXT,
                    reaction_info TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(vk_chat_id, message_id)
                )
            """)
            
            # Статистика по дням
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_stats (
                    vk_chat_id TEXT,
                    date TEXT,
                    message_count INTEGER,
                    unique_senders INTEGER,
                    first_message_time INTEGER,
                    last_message_time INTEGER,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (vk_chat_id, date)
                )
            """)
            
            # Суммаризации
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vk_chat_id TEXT,
                    date TEXT,
                    summary_text TEXT,
                    summary_type TEXT DEFAULT 'daily',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(vk_chat_id, date, summary_type)
                )
            """)
            
            # Сообщения бота в группах
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS group_messages (
                    group_id INTEGER,
                    vk_chat_id TEXT,
                    date TEXT,
                    message_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (group_id, vk_chat_id, date)
                )
            """)
            
            # Создание индексов для производительности
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_chat_date ON messages(vk_chat_id, date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_time ON messages(message_time)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_stats_chat ON daily_stats(vk_chat_id)")
            
            conn.commit()
            logger.info("База данных инициализирована")
    
    def add_user(self, user_id: int, username: str = None, is_admin: bool = False):
        """Добавить пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO users (user_id, username, is_admin)
                VALUES (?, ?, ?)
            """, (user_id, username, is_admin))
            conn.commit()
    
    def add_group(self, group_id: int, group_name: str):
        """Добавить группу"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO groups (group_id, group_name)
                VALUES (?, ?)
            """, (group_id, group_name))
            conn.commit()
    
    def add_group_user(self, group_id: int, user_id: int, is_admin: bool = False):
        """Добавить пользователя в группу"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO group_users (group_id, user_id, is_admin)
                VALUES (?, ?, ?)
            """, (group_id, user_id, is_admin))
            conn.commit()
    
    def get_user_groups(self, user_id: int) -> List[Dict]:
        """Получить группы пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT g.group_id, g.group_name, gu.is_admin
                FROM groups g
                JOIN group_users gu ON g.group_id = gu.group_id
                WHERE gu.user_id = ?
            """, (user_id,))
            return [{"group_id": row[0], "group_name": row[1], "is_admin": row[2]} for row in cursor.fetchall()]
    
    def get_all_groups(self) -> List[Dict]:
        """Получить все группы, где есть бот"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT group_id, group_name
                FROM groups
                ORDER BY group_name
            """)
            return [{"group_id": row[0], "group_name": row[1]} for row in cursor.fetchall()]
    
    def get_vk_chat_info(self, vk_chat_id: str) -> Optional[Dict]:
        """Получить информацию о VK чате"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT chat_id, chat_name
                FROM vk_chats
                WHERE chat_id = ?
            """, (vk_chat_id,))
            result = cursor.fetchone()
            if result:
                return {
                    "chat_id": result[0],
                    "chat_name": result[1]
                }
            return None
    
    def add_vk_chat(self, chat_id: str, chat_name: str, chat_type: str = "chat"):
        """Добавить чат VK MAX"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO vk_chats (chat_id, chat_name, chat_type)
                VALUES (?, ?, ?)
            """, (chat_id, chat_name, chat_type))
            conn.commit()
    
    def add_group_vk_chat(self, group_id: int, vk_chat_id: str, added_by: int):
        """Связать группу с чатом VK MAX"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO group_vk_chats (group_id, vk_chat_id, added_by)
                VALUES (?, ?, ?)
            """, (group_id, vk_chat_id, added_by))
            conn.commit()
    
    def get_group_vk_chats(self, group_id: int) -> List[Dict]:
        """Получить чаты VK MAX для группы"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT vc.chat_id, vc.chat_name, vc.chat_type
                FROM vk_chats vc
                JOIN group_vk_chats gvc ON vc.chat_id = gvc.vk_chat_id
                WHERE gvc.group_id = ?
            """, (group_id,))
            return [{"chat_id": row[0], "chat_name": row[1], "chat_type": row[2]} for row in cursor.fetchall()]
    
    def save_messages(self, vk_chat_id: str, messages: List[Dict]):
        """Сохранить сообщения в базу данных"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for message in messages:
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO messages (
                            vk_chat_id, message_id, sender_id, sender_name, text,
                            message_time, date, message_type, attachments, reaction_info
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        vk_chat_id,
                        message.get('message_id', ''),
                        message.get('sender_id'),
                        message.get('sender_name', ''),
                        message.get('text', ''),
                        message.get('message_time'),
                        message.get('date', ''),
                        message.get('message_type', 'USER'),
                        json.dumps(message.get('attachments', [])),
                        json.dumps(message.get('reaction_info', {}))
                    ))
                except Exception as e:
                    logger.error(f"Ошибка сохранения сообщения: {e}")
            
            conn.commit()
    
    def get_chat_stats(self, vk_chat_id: str) -> Dict:
        """Получить статистику чата"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Общее количество сообщений
            cursor.execute("SELECT COUNT(*) FROM messages WHERE vk_chat_id = ?", (vk_chat_id,))
            total_messages = cursor.fetchone()[0]
            
            # Количество дней с сообщениями
            cursor.execute("SELECT COUNT(DISTINCT date) FROM messages WHERE vk_chat_id = ?", (vk_chat_id,))
            days_count = cursor.fetchone()[0]
            
            # Последние 5 дней
            cursor.execute("""
                SELECT date, COUNT(*) as message_count
                FROM messages 
                WHERE vk_chat_id = ?
                GROUP BY date
                ORDER BY date DESC
                LIMIT 5
            """, (vk_chat_id,))
            recent_days = [{"date": row[0], "count": row[1]} for row in cursor.fetchall()]
            
            return {
                "total_messages": total_messages,
                "days_count": days_count,
                "recent_days": recent_days
            }
    
    def save_summary(self, vk_chat_id: str, date: str, summary_text: str, summary_type: str = "daily"):
        """Сохранить суммаризацию"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO summaries (vk_chat_id, date, summary_text, summary_type)
                VALUES (?, ?, ?, ?)
            """, (vk_chat_id, date, summary_text, summary_type))
            conn.commit()
    
    def get_summary(self, vk_chat_id: str, date: str, summary_type: str = "daily") -> Optional[str]:
        """Получить суммаризацию"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT summary_text FROM summaries
                WHERE vk_chat_id = ? AND date = ? AND summary_type = ?
            """, (vk_chat_id, date, summary_type))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def get_messages_by_date(self, vk_chat_id: str, date: str) -> List[Dict]:
        """Получить сообщения за определенную дату"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT message_id, sender_id, sender_name, text, message_time, 
                       message_type, attachments, reaction_info
                FROM messages 
                WHERE vk_chat_id = ? AND date = ?
                ORDER BY message_time ASC
            """, (vk_chat_id, date))
            
            messages = []
            for row in cursor.fetchall():
                message = {
                    "message_id": row[0],
                    "sender_id": row[1],
                    "sender_name": row[2],
                    "text": row[3],
                    "message_time": row[4],
                    "message_type": row[5],
                    "attachments": json.loads(row[6]) if row[6] else [],
                    "reaction_info": json.loads(row[7]) if row[7] else {}
                }
                messages.append(message)
            
            return messages
    
    def get_last_message_timestamp(self, vk_chat_id: str) -> Optional[int]:
        """Получить timestamp последнего сообщения в чате"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT message_time FROM messages 
                WHERE vk_chat_id = ? 
                ORDER BY message_time DESC 
                LIMIT 1
            """, (vk_chat_id,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def get_available_summaries(self, vk_chat_id: str) -> List[Dict]:
        """Получить список доступных суммаризаций для чата"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT date, summary_type, created_at
                FROM summaries 
                WHERE vk_chat_id = ?
                ORDER BY date DESC
            """, (vk_chat_id,))
            
            summaries = []
            for row in cursor.fetchall():
                summaries.append({
                    "date": row[0],
                    "summary_type": row[1],
                    "created_at": row[2]
                })
            
            return summaries
    
    def update_group_message(self, group_id: int, vk_chat_id: str, date: str, message_id: int):
        """Обновить сообщение в группе"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO group_messages (group_id, vk_chat_id, date, message_id)
                VALUES (?, ?, ?, ?)
            """, (group_id, vk_chat_id, date, message_id))
            conn.commit()
    
    def get_group_message(self, group_id: int, vk_chat_id: str, date: str) -> Optional[int]:
        """Получить message_id для обновления"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT message_id FROM group_messages
                WHERE group_id = ? AND vk_chat_id = ? AND date = ?
            """, (group_id, vk_chat_id, date))
            result = cursor.fetchone()
            return result[0] if result else None
