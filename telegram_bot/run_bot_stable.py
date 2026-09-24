#!/usr/bin/env python3
"""
Стабильная версия запуска бота
"""
import asyncio
import logging
import signal
import sys
from bot import VKMaxTelegramBot

# Настройка логирования
logging.basicConfig(
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

class BotRunner:
    """Класс для стабильного запуска бота"""
    
    def __init__(self):
        self.bot = None
        self.running = False
    
    async def start(self):
        """Запуск бота"""
        try:
            logger.info("🤖 Запуск VK MAX Telegram Bot")
            self.bot = VKMaxTelegramBot()
            self.running = True
            
            # Запускаем бота
            await self.bot.start_polling()
            
        except KeyboardInterrupt:
            logger.info("🛑 Получен сигнал остановки")
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")
        finally:
            await self.stop()
    
    async def stop(self):
        """Остановка бота"""
        if self.bot and self.running:
            try:
                await self.bot.stop()
                logger.info("👋 Бот остановлен")
            except Exception as e:
                logger.error(f"❌ Ошибка остановки: {e}")
            finally:
                self.running = False

async def main():
    """Главная функция"""
    runner = BotRunner()
    
    # Обработка сигналов
    def signal_handler(signum, frame):
        logger.info("🛑 Получен сигнал остановки")
        asyncio.create_task(runner.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await runner.start()
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
    finally:
        logger.info("👋 Завершение работы")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
