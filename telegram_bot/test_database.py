#!/usr/bin/env python3
"""
Тест базы данных для Telegram бота
"""
import os
import tempfile
from database import DatabaseManager

def test_database():
    """Тестирование функциональности базы данных"""
    print("🧪 Тестирование базы данных...")
    
    # Создаем временную базу данных
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        # Инициализируем базу данных
        db = DatabaseManager(db_path)
        print("✅ База данных создана")
        
        # Тестируем добавление пользователя
        db.add_user(12345, "test_user", is_admin=True)
        print("✅ Пользователь добавлен")
        
        # Тестируем добавление группы
        db.add_group(67890, "Test Group")
        print("✅ Группа добавлена")
        
        # Тестируем связь пользователя с группой
        db.add_group_user(67890, 12345, is_admin=True)
        print("✅ Связь пользователь-группа создана")
        
        # Тестируем получение групп пользователя
        user_groups = db.get_user_groups(12345)
        print(f"✅ Группы пользователя: {user_groups}")
        
        # Тестируем добавление чата VK MAX
        db.add_vk_chat("test_chat_123", "Test Chat", "CHAT")
        print("✅ Чат VK MAX добавлен")
        
        # Тестируем связь группы с чатом
        db.add_group_vk_chat(67890, "test_chat_123", 12345)
        print("✅ Связь группа-чат создана")
        
        # Тестируем получение чатов группы
        group_chats = db.get_group_vk_chats(67890)
        print(f"✅ Чаты группы: {group_chats}")
        
        # Тестируем добавление сообщений
        test_messages = [
            {
                "message_id": "msg_1",
                "sender_id": 111,
                "sender_name": "User1",
                "text": "Test message 1",
                "message_time": 1640995200000,  # 2022-01-01
                "date": "2022-01-01",
                "message_type": "USER",
                "attachments": [],
                "reaction_info": {}
            },
            {
                "message_id": "msg_2", 
                "sender_id": 222,
                "sender_name": "User2",
                "text": "Test message 2",
                "message_time": 1640995260000,  # 2022-01-01
                "date": "2022-01-01",
                "message_type": "USER",
                "attachments": [],
                "reaction_info": {}
            }
        ]
        
        db.save_messages("test_chat_123", test_messages)
        print("✅ Сообщения сохранены")
        
        # Тестируем получение статистики
        stats = db.get_chat_stats("test_chat_123")
        print(f"✅ Статистика чата: {stats}")
        
        # Тестируем сохранение суммаризации
        db.save_summary("test_chat_123", "2022-01-01", "Test summary", "daily")
        print("✅ Суммаризация сохранена")
        
        # Тестируем получение суммаризации
        summary = db.get_summary("test_chat_123", "2022-01-01")
        print(f"✅ Суммаризация получена: {summary}")
        
        print("\n🎉 Все тесты базы данных пройдены успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False
    finally:
        # Удаляем временную базу данных
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    return True

if __name__ == "__main__":
    test_database()
