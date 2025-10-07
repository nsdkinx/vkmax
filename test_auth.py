#!/usr/bin/env python3
"""
Тест различных форматов авторизации для GigaChat
"""

import requests
import base64
import urllib3
from pathlib import Path
import os

# Отключаем предупреждения о SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_auth_formats():
    """Тест различных форматов авторизации"""
    
    # Загружаем API ключ
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    
    api_key = os.getenv('GIGACHAT_API_KEY')
    if not api_key:
        print("❌ API ключ не найден")
        return
    
    # Декодируем ключ
    try:
        decoded_key = base64.b64decode(api_key).decode('utf-8')
        print(f"🔑 Декодированный ключ: {decoded_key}")
    except Exception as e:
        print(f"❌ Ошибка декодирования: {e}")
        return
    
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    
    data = {
        "model": "GigaChat:latest",
        "messages": [{"role": "user", "content": "Привет!"}],
        "temperature": 0.7,
        "max_tokens": 50
    }
    
    # Тест 1: Bearer с оригинальным ключом
    print("\n🧪 Тест 1: Bearer с оригинальным ключом")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    test_request(url, headers, data)
    
    # Тест 2: Bearer с декодированным ключом
    print("\n🧪 Тест 2: Bearer с декодированным ключом")
    headers = {
        "Authorization": f"Bearer {decoded_key}",
        "Content-Type": "application/json"
    }
    test_request(url, headers, data)
    
    # Тест 3: Basic Auth с декодированным ключом
    print("\n🧪 Тест 3: Basic Auth с декодированным ключом")
    auth_string = base64.b64encode(decoded_key.encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_string}",
        "Content-Type": "application/json"
    }
    test_request(url, headers, data)
    
    # Тест 4: X-API-Key заголовок
    print("\n🧪 Тест 4: X-API-Key заголовок")
    headers = {
        "X-API-Key": decoded_key,
        "Content-Type": "application/json"
    }
    test_request(url, headers, data)

def test_request(url, headers, data):
    """Тест запроса с заданными заголовками"""
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30, verify=False)
        print(f"   📡 Статус: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Успех!")
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                print(f"   🤖 Ответ: {content[:50]}...")
        else:
            print(f"   ❌ Ошибка: {response.text}")
    except Exception as e:
        print(f"   ❌ Исключение: {e}")

if __name__ == "__main__":
    test_auth_formats()
