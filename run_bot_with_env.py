#!/usr/bin/env python3
"""
🚀 ЗАПУСК TELEGRAM БОТА С АВТОМАТИЧЕСКОЙ ЗАГРУЗКОЙ ТОКЕНОВ
Запуск: python run_bot_with_env.py
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

# Загружаем переменные из конфигурационного файла
def load_env():
    """Загрузить переменные из конфигурационного файла"""
    # Пробуем разные файлы конфигурации
    config_files = ['.env', 'bot_config.env', 'telegram_bot/.env']
    
    for config_file in config_files:
        env_file = Path(config_file)
        if env_file.exists():
            print(f"📁 Загружаем конфигурацию из: {config_file}")
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
            return True
    
    print("⚠️  Конфигурационный файл не найден")
    return False

# Загружаем переменные окружения
load_env()

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
    gigachat_key = os.getenv("GIGACHAT_API_KEY")
    
    print(f"📋 Проверка токенов:")
    print(f"   TELEGRAM_BOT_TOKEN: {'✅ Установлен' if telegram_token else '❌ Не установлен'}")
    print(f"   VK_MAX_TOKEN: {'✅ Установлен' if vk_max_token else '❌ Не установлен'}")
    print(f"   GIGACHAT_API_KEY: {'✅ Установлен' if gigachat_key else '❌ Не установлен'}")
    
    if not telegram_token:
        print("\n❌ TELEGRAM_BOT_TOKEN не установлен!")
        print("💡 Создайте файл .env с токенами:")
        print("   TELEGRAM_BOT_TOKEN=ваш_токен")
        print("   VK_MAX_TOKEN=ваш_токен")
        print("   GIGACHAT_API_KEY=ваш_ключ")
        return
    
    if not vk_max_token:
        print("\n❌ VK_MAX_TOKEN не установлен!")
        print("💡 Добавьте в .env файл: VK_MAX_TOKEN=ваш_токен")
        return
    
    print("\n✅ Токены проверены")
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
