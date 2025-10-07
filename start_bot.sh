#!/bin/bash
# 🚀 ЕДИНЫЙ ФАЙЛ ЗАПУСКА TELEGRAM БОТА
# Автоматически активирует виртуальное окружение и запускает бота

echo "🤖 ЗАПУСК TELEGRAM БОТА ДЛЯ VK MAX"
echo "=================================="

# Переходим в директорию проекта
cd "$(dirname "$0")"

# Проверяем существование виртуального окружения
if [ ! -d "venv" ]; then
    echo "❌ Виртуальное окружение не найдено!"
    echo "💡 Создайте виртуальное окружение: python -m venv venv"
    exit 1
fi

# Проверяем существование файла конфигурации
if [ ! -f ".env" ] && [ ! -f "bot_config.env" ]; then
    echo "❌ Файл конфигурации не найден!"
    echo "💡 Создайте файл .env с токенами:"
    echo "   TELEGRAM_BOT_TOKEN=ваш_токен"
    echo "   VK_MAX_TOKEN=ваш_токен"
    echo "   GIGACHAT_API_KEY=ваш_ключ"
    exit 1
fi

echo "📁 Активируем виртуальное окружение..."
source venv/bin/activate

echo "📦 Проверяем зависимости..."
# Проверяем и устанавливаем зависимости если нужно
if ! python -c "import telegram" 2>/dev/null; then
    echo "📥 Устанавливаем зависимости..."
    pip install -r requirements.txt
fi

echo "🚀 Запускаем бота..."
python run_bot_with_env.py
