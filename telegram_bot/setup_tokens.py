#!/usr/bin/env python3
"""
Скрипт для настройки токенов
"""
import os

def setup_tokens():
    """Настройка токенов"""
    print("🔧 НАСТРОЙКА ТОКЕНОВ ДЛЯ TELEGRAM БОТА")
    print("=" * 50)
    
    # Проверяем текущие токены
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    gigachat_key = os.getenv("GIGACHAT_API_KEY")
    vk_max_token = os.getenv("VK_MAX_TOKEN")
    
    print(f"📋 Текущие токены:")
    print(f"   TELEGRAM_BOT_TOKEN: {telegram_token[:20] + '...' if telegram_token and len(telegram_token) > 20 else telegram_token}")
    print(f"   GIGACHAT_API_KEY: {gigachat_key[:20] + '...' if gigachat_key and len(gigachat_key) > 20 else gigachat_key}")
    print(f"   VK_MAX_TOKEN: {vk_max_token[:20] + '...' if vk_max_token and len(vk_max_token) > 20 else vk_max_token}")
    
    print("\n💡 Для запуска бота установите реальные токены:")
    print("   export TELEGRAM_BOT_TOKEN='ваш_реальный_telegram_токен'")
    print("   export GIGACHAT_API_KEY='ваш_реальный_gigachat_ключ'")
    print("   export VK_MAX_TOKEN='ваш_vk_max_токен'")
    
    print("\n🚀 После установки токенов запустите:")
    print("   python start_with_tokens.py")
    
    # Проверяем, есть ли реальные токены
    if telegram_token and telegram_token != "your_real_token_here":
        print("\n✅ TELEGRAM_BOT_TOKEN выглядит как реальный токен")
    else:
        print("\n❌ TELEGRAM_BOT_TOKEN не установлен или является заглушкой")
    
    if gigachat_key and gigachat_key != "your_real_key_here":
        print("✅ GIGACHAT_API_KEY выглядит как реальный ключ")
    else:
        print("❌ GIGACHAT_API_KEY не установлен или является заглушкой")
    
    if vk_max_token and len(vk_max_token) > 100:
        print("✅ VK_MAX_TOKEN выглядит как реальный токен")
    else:
        print("❌ VK_MAX_TOKEN не установлен или слишком короткий")

if __name__ == "__main__":
    setup_tokens()
