@echo off
REM 🚀 ЕДИНЫЙ ФАЙЛ ЗАПУСКА TELEGRAM БОТА ДЛЯ WINDOWS
REM Автоматически активирует виртуальное окружение и запускает бота

echo 🤖 ЗАПУСК TELEGRAM БОТА ДЛЯ VK MAX
echo ==================================

REM Переходим в директорию проекта
cd /d "%~dp0"

REM Проверяем существование виртуального окружения
if not exist "venv\Scripts\python.exe" (
    echo ❌ Виртуальное окружение не найдено!
    echo 💡 Создайте виртуальное окружение: python -m venv venv
    pause
    exit /b 1
)

REM Проверяем файл конфигурации
if not exist ".env" if not exist "bot_config.env" (
    echo ❌ Файл конфигурации не найден!
    echo 💡 Создайте файл .env с токенами:
    echo    TELEGRAM_BOT_TOKEN=ваш_токен
    echo    VK_MAX_TOKEN=ваш_токен
    echo    GIGACHAT_API_KEY=ваш_ключ
    pause
    exit /b 1
)

echo 📁 Активируем виртуальное окружение...
call venv\Scripts\activate.bat

echo 📦 Проверяем зависимости...
venv\Scripts\python.exe -c "import telegram" 2>nul
if errorlevel 1 (
    echo 📥 Устанавливаем зависимости...
    venv\Scripts\pip.exe install -r requirements.txt
)

echo 🚀 Запускаем бота...
venv\Scripts\python.exe run_bot_with_env.py

pause
