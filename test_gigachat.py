#!/usr/bin/env python3
"""
Простой тест подключения к GigaChat API
"""

import requests
import json
import urllib3
import os
from pathlib import Path

# Отключаем предупреждения о SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_gigachat_connection():
    """Тест подключения к GigaChat"""
    # Загружаем переменные из .env файла
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    
    api_key = os.getenv('GIGACHAT_API_KEY', "test_api_key_here")
    
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "GigaChat:latest",
        "messages": [
            {
                "role": "user",
                "content": "Привет! Это тест подключения."
            }
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    try:
        print(f"🔗 Тестируем подключение к {url}")
        print(f"🔑 Используем API ключ: {api_key[:10]}...")
        
        response = requests.post(url, headers=headers, json=data, timeout=30, verify=False)
        
        print(f"📡 Статус ответа: {response.status_code}")
        print(f"📋 Заголовки ответа: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Успешное подключение!")
            print(f"📋 Структура ответа: {list(result.keys())}")
            
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                print(f"🤖 Ответ GigaChat: {content}")
            else:
                print(f"❌ Неожиданный формат ответа: {result}")
        else:
            print(f"❌ Ошибка HTTP: {response.status_code}")
            print(f"📋 Текст ответа: {response.text}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print(f"📋 Тип ошибки: {type(e).__name__}")

if __name__ == "__main__":
    test_gigachat_connection()
