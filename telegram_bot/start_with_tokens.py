#!/usr/bin/env python3
"""
Скрипт запуска бота с токенами из переменных окружения
"""
import os
import asyncio
import logging
from bot import VKMaxTelegramBot

# Настройка логирования
logging.basicConfig(
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

async def main():
    """Главная функция"""
    logger.info("🤖 Запуск VK MAX Telegram Bot с токенами")
    
    # Проверяем наличие токенов
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    gigachat_key = os.getenv("GIGACHAT_API_KEY") 
    vk_max_token = os.getenv("VK_MAX_TOKEN")
    
    logger.info(f"📋 Проверка токенов:")
    logger.info(f"   TELEGRAM_BOT_TOKEN: {'✅ Установлен' if telegram_token else '❌ Не установлен'}")
    logger.info(f"   GIGACHAT_API_KEY: {'✅ Установлен' if gigachat_key else '❌ Не установлен'}")
    logger.info(f"   VK_MAX_TOKEN: {'✅ Установлен' if vk_max_token else '❌ Не установлен'}")
    
    if not telegram_token:
        logger.error("❌ TELEGRAM_BOT_TOKEN не установлен")
        logger.info("💡 Установите переменную: export TELEGRAM_BOT_TOKEN='your_token'")
        return
    
    if not vk_max_token:
        logger.error("❌ VK_MAX_TOKEN не установлен")
        logger.info("💡 Установите переменную: export VK_MAX_TOKEN='your_token'")
        return
    
    if not gigachat_key:
        logger.warning("⚠️  GIGACHAT_API_KEY не установлен - анализ чатов недоступен")
        logger.info("💡 Установите переменную: export GIGACHAT_API_KEY='your_key'")
    
    # Создаем и запускаем бота
    bot = VKMaxTelegramBot()
    
    try:
        logger.info("🚀 Запуск бота...")
        await bot.start_polling()
    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал остановки")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
    finally:
        await bot.stop()
        logger.info("👋 Бот остановлен")

if __name__ == "__main__":
    asyncio.run(main())
