#!/usr/bin/env python3
"""
🚀 ЕДИНЫЙ ФАЙЛ ЗАПУСКА TELEGRAM БОТА
Автоматически активирует виртуальное окружение и запускает бота
Запуск: python start_bot.py
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

def main():
    """Главная функция запуска"""
    print("🤖 ЗАПУСК TELEGRAM БОТА ДЛЯ VK MAX")
    print("=" * 40)
    
    # Получаем директорию проекта
    project_dir = Path(__file__).parent.absolute()
    os.chdir(project_dir)
    
    # Определяем путь к виртуальному окружению
    if platform.system() == "Windows":
        venv_python = project_dir / "venv" / "Scripts" / "python.exe"
        venv_activate = project_dir / "venv" / "Scripts" / "activate.bat"
    else:
        venv_python = project_dir / "venv" / "bin" / "python"
        venv_activate = project_dir / "venv" / "bin" / "activate"
    
    # Проверяем существование виртуального окружения
    if not venv_python.exists():
        print("❌ Виртуальное окружение не найдено!")
        print("💡 Создайте виртуальное окружение:")
        print("   python -m venv venv")
        print("   source venv/bin/activate  # Linux/Mac")
        print("   venv\\Scripts\\activate     # Windows")
        return 1
    
    # Проверяем файлы конфигурации
    config_files = [".env", "bot_config.env", "telegram_bot/.env"]
    config_found = False
    
    for config_file in config_files:
        if Path(config_file).exists():
            print(f"📁 Найден файл конфигурации: {config_file}")
            config_found = True
            break
    
    if not config_found:
        print("❌ Файл конфигурации не найден!")
        print("💡 Создайте файл .env с токенами:")
        print("   TELEGRAM_BOT_TOKEN=ваш_токен")
        print("   VK_MAX_TOKEN=ваш_токен")
        print("   GIGACHAT_API_KEY=ваш_ключ")
        return 1
    
    print("📦 Проверяем зависимости...")
    
    # Проверяем установлены ли зависимости
    try:
        result = subprocess.run([
            str(venv_python), "-c", "import telegram, requests, websockets"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("📥 Устанавливаем зависимости...")
            install_result = subprocess.run([
                str(venv_python), "-m", "pip", "install", "-r", "requirements.txt"
            ], capture_output=True, text=True)
            
            if install_result.returncode != 0:
                print(f"❌ Ошибка установки зависимостей: {install_result.stderr}")
                return 1
            print("✅ Зависимости установлены")
        else:
            print("✅ Зависимости уже установлены")
            
    except Exception as e:
        print(f"❌ Ошибка проверки зависимостей: {e}")
        return 1
    
    print("🚀 Запускаем бота...")
    
    # Запускаем бота
    try:
        if platform.system() == "Windows":
            # На Windows используем cmd
            process = subprocess.Popen([
                "cmd", "/c", str(venv_python), "run_bot_with_env.py"
            ])
        else:
            # На Linux/Mac используем bash
            process = subprocess.Popen([
                str(venv_python), "run_bot_with_env.py"
            ])
        
        # Ждем завершения процесса
        process.wait()
        
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен пользователем")
        if 'process' in locals():
            process.terminate()
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        if 'process' in locals():
            process.terminate()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
