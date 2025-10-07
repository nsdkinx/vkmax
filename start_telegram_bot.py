#!/usr/bin/env python3
"""
🚀 ПРОСТОЙ ЗАПУСК TELEGRAM БОТА
Просто запустите: python start_telegram_bot.py
"""
import sys
import os
import asyncio
import logging
from pathlib import Path

# Добавляем путь к telegram_bot в sys.path
current_dir = Path(__file__).parent
telegram_bot_dir = current_dir / "telegram_bot"
sys.path.insert(0, str(telegram_bot_dir))

# Настройка логирования
logging.basicConfig(
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

async def main():
    """Главная функция запуска бота"""
    logger.info("🤖 ЗАПУСК TELEGRAM БОТА ДЛЯ VK MAX")
    logger.info("=" * 50)
    
    try:
        # Импортируем компоненты бота
        from bot import VKMaxTelegramBot
        
        # Проверяем токены
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        gigachat_key = os.getenv("GIGACHAT_API_KEY")
        vk_max_token = os.getenv("VK_MAX_TOKEN")
        
        logger.info("📋 Проверка токенов:")
        logger.info(f"   TELEGRAM_BOT_TOKEN: {'✅ Установлен' if telegram_token else '❌ Не установлен'}")
        logger.info(f"   GIGACHAT_API_KEY: {'✅ Установлен' if gigachat_key else '❌ Не установлен'}")
        logger.info(f"   VK_MAX_TOKEN: {'✅ Установлен' if vk_max_token else '❌ Не установлен'}")
        
        if not telegram_token:
            logger.error("❌ TELEGRAM_BOT_TOKEN не установлен!")
            logger.info("💡 Установите: export TELEGRAM_BOT_TOKEN='ваш_токен'")
            return
        
        if not vk_max_token:
            logger.error("❌ VK_MAX_TOKEN не установлен!")
            logger.info("💡 Установите: export VK_MAX_TOKEN='ваш_токен'")
            return
        
        if not gigachat_key:
            logger.warning("⚠️  GIGACHAT_API_KEY не установлен - анализ чатов недоступен")
            logger.info("💡 Установите: export GIGACHAT_API_KEY='ваш_ключ'")
        
        # Создаем и запускаем бота
        logger.info("🚀 Создание бота...")
        bot = VKMaxTelegramBot()
        
        logger.info("🚀 Запуск бота...")
        await bot.start_polling()
        
    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал остановки")
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        logger.info("💡 Проверьте, что все токены установлены правильно")
    finally:
        logger.info("👋 Бот остановлен")

if __name__ == "__main__":
    print("🤖 TELEGRAM БОТ ДЛЯ VK MAX")
    print("=" * 30)
    print("Запуск...")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)
