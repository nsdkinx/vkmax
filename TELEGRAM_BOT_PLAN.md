# 🤖 ПЛАН РАЗРАБОТКИ TELEGRAM БОТА ДЛЯ АНАЛИЗА ЧАТОВ VK MAX

## 🎯 ЦЕЛЬ ПРОЕКТА

Создание Telegram бота для интеграции с системой анализа чатов VK MAX, который позволит:
- Управлять чатами VK MAX через Telegram интерфейс
- Загружать и анализировать сообщения с сохранением в SQLite
- Публиковать результаты анализа в группы
- Обновлять существующие сообщения в группах

## 🏗️ АРХИТЕКТУРА СИСТЕМЫ

### 📁 Структура проекта
```
telegram_bot/
├── bot.py                 # Основной файл бота
├── database.py           # Работа с SQLite
├── vk_integration.py     # Интеграция с VK MAX API
├── chat_analyzer.py      # Анализ чатов (переиспользование кода)
├── keyboards.py          # Клавиатуры Telegram
├── handlers.py           # Обработчики команд и сообщений
├── config.py             # Конфигурация
├── utils.py              # Вспомогательные функции
├── requirements.txt      # Зависимости
├── bot_database.db      # SQLite база данных
└── README.md            # Документация
```

## 🗄️ СХЕМА БАЗЫ ДАННЫХ SQLITE

### 📊 Основные таблицы

```sql
-- Пользователи бота
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Telegram группы
CREATE TABLE groups (
    group_id INTEGER PRIMARY KEY,
    group_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Связь пользователей с группами (кто может управлять)
CREATE TABLE group_users (
    group_id INTEGER,
    user_id INTEGER,
    is_admin BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (group_id, user_id)
);

-- Чаты VK MAX
CREATE TABLE vk_chats (
    chat_id TEXT PRIMARY KEY,
    chat_name TEXT,
    chat_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Связь групп с чатами VK MAX
CREATE TABLE group_vk_chats (
    group_id INTEGER,
    vk_chat_id TEXT,
    added_by INTEGER,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (group_id, vk_chat_id)
);

-- Сообщения по дням (НОВАЯ ТАБЛИЦА)
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vk_chat_id TEXT NOT NULL,
    message_id TEXT NOT NULL,
    sender_id INTEGER,
    sender_name TEXT,
    text TEXT,
    message_time INTEGER,  -- timestamp
    date TEXT,             -- YYYY-MM-DD
    message_type TEXT,     -- USER, SYSTEM, etc.
    attachments TEXT,      -- JSON array
    reaction_info TEXT,    -- JSON object
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(vk_chat_id, message_id)
);

-- Статистика по дням
CREATE TABLE daily_stats (
    vk_chat_id TEXT,
    date TEXT,
    message_count INTEGER,
    unique_senders INTEGER,
    first_message_time INTEGER,
    last_message_time INTEGER,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (vk_chat_id, date)
);

-- Суммаризации
CREATE TABLE summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vk_chat_id TEXT,
    date TEXT,
    summary_text TEXT,
    summary_type TEXT DEFAULT 'daily',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(vk_chat_id, date, summary_type)
);

-- Сообщения бота в группах (для обновления)
CREATE TABLE group_messages (
    group_id INTEGER,
    vk_chat_id TEXT,
    date TEXT,
    message_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (group_id, vk_chat_id, date)
);

-- Индексы для производительности
CREATE INDEX idx_messages_chat_date ON messages(vk_chat_id, date);
CREATE INDEX idx_messages_sender ON messages(sender_id);
CREATE INDEX idx_messages_time ON messages(message_time);
CREATE INDEX idx_daily_stats_chat ON daily_stats(vk_chat_id);
```

## 🤖 ФУНКЦИОНАЛЬНОСТЬ БОТА

### 📱 Основные сценарии использования

#### 1. **Первоначальная настройка**
```
Пользователь → Добавляет бота в группу
Пользователь → /start в личных сообщениях
Бот → Проверяет группы, где пользователь админ
Бот → Показывает список групп для выбора
Пользователь → Выбирает группу для работы
```

#### 2. **Управление чатами VK MAX**
```
Главное меню:
├── 📊 Управление чатами
│   ├── ➕ Добавить чат
│   ├── ❌ Удалить чат  
│   ├── 📋 Список чатов
│   └── ⚙️ Настройки чата
├── 📈 Статистика
└── 🔧 Настройки
```

#### 3. **Работа с конкретным чатом**
```
Информация о чате:
├── 📊 Статистика: X дней загружено
├── 📅 Последние 5 дней:
│   ├── 2025-10-07 (12 сообщений)
│   ├── 2025-10-06 (67 сообщений)
│   └── ...
├── 🔄 Загрузить сообщения
├── 📋 Проверить суммаризацию
└── 📤 Вывести в группу
```

### 🔄 Система состояний (FSM)

**Состояния бота:**
- `START` - начальное состояние
- `SELECT_GROUP` - выбор группы
- `MANAGE_CHATS` - управление чатами
- `ADD_CHAT` - добавление чата (ввод ID)
- `CHAT_SETTINGS` - настройки чата
- `LOADING_MESSAGES` - загрузка сообщений
- `VIEW_SUMMARY` - просмотр суммаризации
- `PUBLISH_SUMMARY` - публикация в группу

## 🔧 ТЕХНИЧЕСКАЯ РЕАЛИЗАЦИЯ

### 📦 Зависимости
```python
# requirements.txt
python-telegram-bot==20.7
requests==2.32.5
sqlite3  # встроенный
asyncio  # встроенный
pathlib  # встроенный
json     # встроенный
datetime # встроенный
logging  # встроенный
```

### 🔑 Конфигурация
```python
# config.py
TELEGRAM_BOT_TOKEN = "your_bot_token"   # Из .env файла
GIGACHAT_API_KEY = "your_gigachat_key"  # Из .env файла
VK_MAX_TOKEN = "your_vk_max_token"      # Из .env файла
DATABASE_PATH = "bot_database.db"
CHATS_DIR = "../chats"  # Путь к папке с файлами чатов
```

## 📋 ДЕТАЛЬНЫЙ ПЛАН РАЗРАБОТКИ

### **ЭТАП 1: Базовая структура** (2-3 дня)

#### 1.1 Создание структуры проекта
- [ ] Создать папку `telegram_bot/`
- [ ] Настроить `requirements.txt`
- [ ] Создать `config.py` с настройками
- [ ] Настроить логирование

#### 1.2 База данных
- [ ] Создать `database.py` с классом `DatabaseManager`
- [ ] Реализовать `init_database()` - создание всех таблиц
- [ ] Добавить методы для работы с пользователями и группами
- [ ] Создать тесты для БД

#### 1.3 Базовые клавиатуры
- [ ] Создать `keyboards.py`
- [ ] Реализовать главное меню
- [ ] Создать клавиатуры для выбора групп
- [ ] Добавить кнопки навигации

### **ЭТАП 2: Управление группами и чатами** (2-3 дня)

#### 2.1 Система состояний
- [ ] Настроить FSM для бота
- [ ] Реализовать переходы между состояниями
- [ ] Добавить обработку прерываний

#### 2.2 Управление группами
- [ ] Проверка прав администратора в группах
- [ ] Выбор группы для работы
- [ ] Сохранение связи пользователь-группа

#### 2.3 Управление чатами VK MAX
- [ ] Добавление чатов по ID
- [ ] Удаление чатов из списка
- [ ] Просмотр списка привязанных чатов
- [ ] Валидация ID чатов

### **ЭТАП 3: Интеграция с VK MAX** (3-4 дня)

#### 3.1 VK MAX API интеграция
- [ ] Создать `vk_integration.py`
- [ ] Переиспользовать код из `analyze_chat.py`
- [ ] Реализовать загрузку сообщений в БД. Переиспользовать код из `save_chats.py`
- [ ] Добавить обработку ошибок API

#### 3.2 Сохранение в SQLite
- [ ] Реализовать `save_messages()` в БД
- [ ] Группировка сообщений по дням
- [ ] Обновление статистики
- [ ] Обработка дубликатов

#### 3.3 Анализ чатов
- [ ] Создать `chat_analyzer.py`
- [ ] Переиспользовать код анализа из `analyze_chat.py`
- [ ] Интеграция с GigaChat API
- [ ] Сохранение суммаризаций в БД

### **ЭТАП 4: Публикация результатов** (2-3 дня)

#### 4.1 Публикация в группы
- [ ] Отправка суммаризации в группу
- [ ] Сохранение message_id для обновления
- [ ] Обработка ошибок отправки

#### 4.2 Обновление сообщений
- [ ] Редактирование существующих сообщений
- [ ] Fallback на новое сообщение при ошибке
- [ ] Уведомления об успешном обновлении

#### 4.3 Управление контентом
- [ ] Форматирование сообщений для Telegram
- [ ] Ограничения по длине сообщений
- [ ] Разбивка длинных текстов

### **ЭТАП 5: Тестирование и отладка** (2-3 дня)

#### 5.1 Тестирование функциональности
- [ ] Тестирование всех сценариев использования
- [ ] Проверка обработки ошибок
- [ ] Тестирование с большими объемами данных

#### 5.2 Оптимизация
- [ ] Оптимизация запросов к БД
- [ ] Кэширование часто используемых данных
- [ ] Асинхронная обработка длительных операций

#### 5.3 Документация
- [ ] Создание README.md
- [ ] Документация API
- [ ] Инструкции по развертыванию

## 🎯 КЛЮЧЕВЫЕ ФУНКЦИИ МОДУЛЕЙ

### 📁 **bot.py** - Основной файл
```python
# Основные функции:
- Инициализация бота и БД
- Регистрация обработчиков команд
- Настройка FSM состояний
- Запуск polling
- Обработка глобальных ошибок
```

### 📁 **database.py** - Работа с БД
```python
# Основные функции:
- init_database() - создание таблиц
- get_user_groups() - группы пользователя
- add_vk_chat() - добавление чата
- save_messages() - сохранение сообщений
- get_chat_stats() - статистика чата
- save_summary() - сохранение суммаризации
- update_group_message() - обновление сообщения в группе
```

### 📁 **vk_integration.py** - VK MAX API
```python
# Основные функции:
- load_chat_messages() - загрузка сообщений
- get_chat_info() - информация о чате
- check_chat_access() - проверка доступа
- save_messages_to_db() - сохранение в БД
```

### 📁 **chat_analyzer.py** - Анализ чатов
```python
# Переиспользование из analyze_chat.py:
- get_gigachat_token() - получение токена
- call_gigachat_api() - анализ чата
- optimize_text() - оптимизация текста
- analyze_chat_by_date() - анализ за день
```

### 📁 **keyboards.py** - Клавиатуры
```python
# Основные клавиатуры:
- main_menu_keyboard() - главное меню
- group_selection_keyboard() - выбор группы
- chat_management_keyboard() - управление чатами
- chat_settings_keyboard() - настройки чата
- back_keyboard() - кнопка "Назад"
```

### 📁 **handlers.py** - Обработчики
```python
# Основные обработчики:
- start_handler() - команда /start
- group_selection_handler() - выбор группы
- add_chat_handler() - добавление чата
- load_messages_handler() - загрузка сообщений
- view_summary_handler() - просмотр суммаризации
- publish_summary_handler() - публикация в группу
```

## ⚠️ КРИТИЧЕСКИЕ МОМЕНТЫ

### 🔒 Безопасность
- Проверка прав администратора в группах
- Валидация входных данных (ID чатов)
- Ограничения на размер загружаемых данных
- Защита от спама и злоупотреблений

### 🚀 Производительность
- Асинхронная обработка API запросов
- Индексы в БД для быстрого поиска
- Кэширование часто используемых данных
- Прогресс-бары для длительных операций

### 🔄 Надежность
- Обработка сетевых ошибок
- Retry логика для API запросов
- Сохранение состояния при ошибках
- Логирование для отладки
- Резервное копирование БД

## 📊 ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ

После реализации бот позволит:
- ✅ Управлять чатами VK MAX через удобный Telegram интерфейс
- ✅ Автоматически загружать и анализировать сообщения
- ✅ Сохранять данные в SQLite для быстрого доступа
- ✅ Публиковать результаты в группы с возможностью обновления
- ✅ Получать уведомления о статусе операций
- ✅ Просматривать статистику по чатам и дням
- ✅ Работать с большими объемами данных эффективно

**Общее время разработки: 10-15 дней**

## 🚀 ПЛАН ЗАПУСКА

1. **Подготовка окружения** (1 день)
2. **Разработка по этапам** (10-15 дней)
3. **Тестирование** (2-3 дня)
4. **Развертывание** (1 день)
5. **Мониторинг и поддержка** (постоянно)
