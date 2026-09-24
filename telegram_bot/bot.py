"""
Основной файл Telegram бота для анализа чатов VK MAX
"""
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from config import *
from database import DatabaseManager
from vk_integration import VKMaxIntegration
from chat_analyzer import ChatAnalyzer
from handlers import BotHandlers

# Настройка логирования
logging.basicConfig(
    format=LOG_FORMAT,
    level=getattr(logging, LOG_LEVEL),
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

class VKMaxTelegramBot:
    """Основной класс Telegram бота"""
    
    def __init__(self):
        self.db = DatabaseManager(DATABASE_PATH)
        self.vk = VKMaxIntegration(VK_MAX_TOKEN)
        self.analyzer = ChatAnalyzer(GIGACHAT_API_KEY)
        self.handlers = BotHandlers(self.db, self.vk, self.analyzer)
        self.application = None
    
    def create_application(self):
        """Создать приложение Telegram"""
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Регистрируем обработчики
        self.application.add_handler(CommandHandler("start", self.handlers.start_handler))
        self.application.add_handler(CallbackQueryHandler(self.handlers.callback_query_handler))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handlers.message_handler))
        
        # Обработчик ошибок
        self.application.add_error_handler(self.error_handler)
        
        logger.info("✅ Обработчики зарегистрированы")
    
    async def error_handler(self, update: Update, context):
        """Обработчик ошибок"""
        logger.error(f"Ошибка при обработке обновления: {context.error}")
        
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "❌ Произошла ошибка. Попробуйте позже."
                )
            except Exception as e:
                logger.error(f"Ошибка отправки сообщения об ошибке: {e}")
    
    async def start_polling(self):
        """Запустить бота в режиме polling"""
        if not self.application:
            self.create_application()
        
        logger.info("🚀 Запуск Telegram бота...")
        
        try:
            # Запускаем бота
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            logger.info("✅ Бот запущен и работает")
            
            # Ждем бесконечно, пока бот работает
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("🛑 Получен сигнал остановки")
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска бота: {e}")
        finally:
            # Очистка ресурсов
            if self.application:
                try:
                    await self.application.stop()
                    await self.application.shutdown()
                except Exception as e:
                    logger.error(f"Ошибка при остановке: {e}")
    
    async def stop(self):
        """Остановить бота"""
        if self.application:
            await self.application.stop()
            await self.application.shutdown()
        logger.info("🛑 Бот остановлен")

async def main():
    """Главная функция"""
    logger.info("🤖 Инициализация VK MAX Telegram Bot")
    
    # Проверяем конфигурацию
    if TELEGRAM_BOT_TOKEN == "your_bot_token":
        logger.error("❌ Не установлен TELEGRAM_BOT_TOKEN")
        return
    
    if VK_MAX_TOKEN == "your_vk_max_token":
        logger.error("❌ Не установлен VK_MAX_TOKEN")
        return
    
    if GIGACHAT_API_KEY == "your_gigachat_key":
        logger.warning("⚠️  Не установлен GIGACHAT_API_KEY - анализ чатов недоступен")
    
    # Создаем и запускаем бота
    bot = VKMaxTelegramBot()
    
    try:
        await bot.start_polling()
    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал остановки")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
    finally:
        await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())
