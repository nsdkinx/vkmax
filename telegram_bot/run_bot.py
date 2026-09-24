#!/usr/bin/env python3
"""
Скрипт запуска Telegram бота
"""
import sys
import os
from pathlib import Path

# Добавляем родительскую директорию в путь для импорта vkmax
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Импортируем и запускаем бота
from telegram_bot.bot import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
