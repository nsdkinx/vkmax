#!/usr/bin/env python3
"""
🚀 ПРОСТОЙ ЗАПУСК TELEGRAM БОТА
Запуск: python run_bot.py
"""
import sys
import os
import asyncio
import logging
from pathlib import Path

# Добавляем путь к telegram_bot
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

def main():
    """Главная функция"""
    print("🤖 TELEGRAM БОТ ДЛЯ VK MAX")
    print("=" * 30)
    
    # Проверяем токены
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    vk_max_token = os.getenv("VK_MAX_TOKEN")
    
    if not telegram_token:
        print("❌ TELEGRAM_BOT_TOKEN не установлен!")
        print("💡 Установите: export TELEGRAM_BOT_TOKEN='ваш_токен'")
        return
    
    if not vk_max_token:
        print("❌ VK_MAX_TOKEN не установлен!")
        print("💡 Установите: export VK_MAX_TOKEN='ваш_токен'")
        return
    
    print("✅ Токены проверены")
    print("🚀 Запуск бота...")
    
    try:
        # Импортируем и запускаем бота
        from bot import VKMaxTelegramBot
        
        async def run_bot():
            bot = VKMaxTelegramBot()
            await bot.start_polling()
        
        asyncio.run(run_bot())
        
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        print("💡 Проверьте токены и попробуйте снова")

if __name__ == "__main__":
    main()
