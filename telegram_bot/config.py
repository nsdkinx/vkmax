"""
Конфигурация для Telegram бота
"""
import os
from pathlib import Path

# Загружаем переменные из .env файла
def load_env():
    """Загрузить переменные из .env файла"""
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# Загружаем переменные окружения
load_env()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "your_bot_token")
GIGACHAT_API_KEY = os.getenv("GIGACHAT_API_KEY", "your_gigachat_key")
VK_MAX_TOKEN = os.getenv("VK_MAX_TOKEN", "your_vk_max_token")

# Database Configuration
DATABASE_PATH = "bot_database.db"
CHATS_DIR = "../chats"  # Путь к папке с файлами чатов

# Bot Settings
ADMIN_USER_IDS = []  # Список ID администраторов бота
MAX_MESSAGE_LENGTH = 4096  # Максимальная длина сообщения Telegram
MAX_MESSAGES_PER_LOAD = 1000  # Максимальное количество сообщений за одну загрузку

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(message)s"
