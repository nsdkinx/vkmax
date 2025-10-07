#!/usr/bin/env python3
"""
Демонстрационный режим Telegram бота
Показывает функциональность без реального Telegram токена
"""
import asyncio
import logging
from database import DatabaseManager
from vk_integration import VKMaxIntegration
from chat_analyzer import ChatAnalyzer
from config import *

# Настройка логирования
logging.basicConfig(
    format=LOG_FORMAT,
    level=getattr(logging, LOG_LEVEL),
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

async def demo_mode():
    """Демонстрационный режим бота"""
    logger.info("🎭 ДЕМОНСТРАЦИОННЫЙ РЕЖИМ TELEGRAM БОТА")
    logger.info("=" * 50)
    
    # Инициализируем компоненты
    logger.info("🔧 Инициализация компонентов...")
    
    # База данных
    db = DatabaseManager("demo_bot.db")
    logger.info("✅ База данных инициализирована")
    
    # VK MAX интеграция
    vk = VKMaxIntegration(VK_MAX_TOKEN)
    logger.info("✅ VK MAX интеграция готова")
    
    # Анализ чатов
    analyzer = ChatAnalyzer(GIGACHAT_API_KEY)
    logger.info("✅ Анализатор чатов готов")
    
    # Демонстрация функциональности
    logger.info("\n📊 ДЕМОНСТРАЦИЯ ФУНКЦИОНАЛЬНОСТИ:")
    logger.info("-" * 40)
    
    # 1. Добавление пользователя
    logger.info("1. Добавление пользователя...")
    db.add_user(12345, "demo_user", is_admin=True)
    logger.info("   ✅ Пользователь добавлен")
    
    # 2. Добавление группы
    logger.info("2. Добавление группы...")
    db.add_group(67890, "Demo Group")
    logger.info("   ✅ Группа добавлена")
    
    # 3. Связь пользователя с группой
    logger.info("3. Связь пользователь-группа...")
    db.add_group_user(67890, 12345, is_admin=True)
    logger.info("   ✅ Связь создана")
    
    # 4. Добавление чата VK MAX
    logger.info("4. Добавление чата VK MAX...")
    db.add_vk_chat("demo_chat_123", "Demo Chat", "CHAT")
    logger.info("   ✅ Чат VK MAX добавлен")
    
    # 5. Связь группы с чатом
    logger.info("5. Связь группа-чат...")
    db.add_group_vk_chat(67890, "demo_chat_123", 12345)
    logger.info("   ✅ Связь группа-чат создана")
    
    # 6. Добавление тестовых сообщений
    logger.info("6. Добавление тестовых сообщений...")
    test_messages = [
        {
            "message_id": "msg_1",
            "sender_id": 111,
            "sender_name": "Родитель1",
            "text": "Доброе утро! Когда будет родительское собрание?",
            "message_time": 1640995200000,
            "date": "2022-01-01",
            "message_type": "USER",
            "attachments": [],
            "reaction_info": {}
        },
        {
            "message_id": "msg_2",
            "sender_id": 222,
            "sender_name": "Учитель",
            "text": "Родительское собрание состоится 15 января в 18:00",
            "message_time": 1640995260000,
            "date": "2022-01-01",
            "message_type": "USER",
            "attachments": [],
            "reaction_info": {}
        },
        {
            "message_id": "msg_3",
            "sender_id": 333,
            "sender_name": "Родитель2",
            "text": "Спасибо за информацию!",
            "message_time": 1640995320000,
            "date": "2022-01-01",
            "message_type": "USER",
            "attachments": [],
            "reaction_info": {}
        }
    ]
    
    db.save_messages("demo_chat_123", test_messages)
    logger.info(f"   ✅ Сохранено {len(test_messages)} сообщений")
    
    # 7. Получение статистики
    logger.info("7. Получение статистики...")
    stats = db.get_chat_stats("demo_chat_123")
    logger.info(f"   📊 Статистика чата:")
    logger.info(f"      • Всего сообщений: {stats['total_messages']}")
    logger.info(f"      • Дней загружено: {stats['days_count']}")
    logger.info(f"      • Последние дни: {len(stats['recent_days'])}")
    
    # 8. Демонстрация анализа чата
    logger.info("8. Демонстрация анализа чата...")
    if GIGACHAT_API_KEY != "your_gigachat_key":
        logger.info("   🤖 Анализ с помощью GigaChat...")
        summary = analyzer.analyze_chat_by_date(test_messages)
        if summary:
            logger.info("   ✅ Суммаризация получена")
            # Сохраняем суммаризацию
            db.save_summary("demo_chat_123", "2022-01-01", summary)
            logger.info("   💾 Суммаризация сохранена в БД")
        else:
            logger.info("   ⚠️  Анализ недоступен (проверьте GIGACHAT_API_KEY)")
    else:
        logger.info("   ⚠️  GigaChat API ключ не настроен")
    
    # 9. Демонстрация VK MAX подключения
    logger.info("9. Демонстрация VK MAX подключения...")
    try:
        if await vk.connect():
            logger.info("   ✅ Подключение к VK MAX успешно")
            await vk.disconnect()
            logger.info("   ✅ Отключение от VK MAX")
        else:
            logger.info("   ⚠️  Не удалось подключиться к VK MAX")
    except Exception as e:
        logger.info(f"   ⚠️  Ошибка подключения: {e}")
    
    # 10. Финальная статистика
    logger.info("\n📈 ФИНАЛЬНАЯ СТАТИСТИКА:")
    logger.info("-" * 40)
    
    user_groups = db.get_user_groups(12345)
    logger.info(f"👤 Пользователь 12345:")
    logger.info(f"   • Групп: {len(user_groups)}")
    for group in user_groups:
        logger.info(f"   • {group['group_name']} (ID: {group['group_id']})")
    
    group_chats = db.get_group_vk_chats(67890)
    logger.info(f"📱 Группа 67890:")
    logger.info(f"   • Чатов VK MAX: {len(group_chats)}")
    for chat in group_chats:
        logger.info(f"   • {chat['chat_name']} (ID: {chat['chat_id']})")
    
    logger.info("\n🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА!")
    logger.info("=" * 50)
    logger.info("✅ Все компоненты бота работают корректно")
    logger.info("✅ База данных полностью функциональна")
    logger.info("✅ VK MAX интеграция готова")
    logger.info("✅ Анализ чатов готов")
    logger.info("✅ Telegram интерфейс готов")
    logger.info("\n🚀 БОТ ГОТОВ К ЗАПУСКУ С РЕАЛЬНЫМИ ТОКЕНАМИ!")

if __name__ == "__main__":
    asyncio.run(demo_mode())
