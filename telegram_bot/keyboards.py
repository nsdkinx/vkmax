"""
Клавиатуры для Telegram бота
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard():
    """Главное меню"""
    keyboard = [
        [InlineKeyboardButton("📊 Управление чатами", callback_data="manage_chats")],
        [InlineKeyboardButton("📈 Статистика", callback_data="statistics")],
        [InlineKeyboardButton("🔧 Настройки", callback_data="settings")],
        [InlineKeyboardButton("🔄 Сменить группу", callback_data="change_group")]
    ]
    return InlineKeyboardMarkup(keyboard)

def group_selection_keyboard(groups: list):
    """Клавиатура выбора группы"""
    keyboard = []
    for group in groups:
        keyboard.append([InlineKeyboardButton(
            f"📱 {group['group_name']}", 
            callback_data=f"select_group_{group['group_id']}"
        )])
    keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="cancel")])
    return InlineKeyboardMarkup(keyboard)

def chat_management_keyboard():
    """Клавиатура управления чатами"""
    keyboard = [
        [InlineKeyboardButton("➕ Добавить чат", callback_data="add_chat")],
        [InlineKeyboardButton("❌ Удалить чат", callback_data="remove_chat")],
        [InlineKeyboardButton("📋 Список чатов", callback_data="list_chats")],
        [InlineKeyboardButton("⚙️ Настройки чата", callback_data="chat_settings")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def chat_list_keyboard(chats: list):
    """Клавиатура списка чатов"""
    keyboard = []
    for chat in chats:
        keyboard.append([InlineKeyboardButton(
            f"💬 {chat['chat_name']}", 
            callback_data=f"select_chat_{chat['chat_id']}"
        )])
    
    # Добавляем кнопку добавления чата
    keyboard.append([InlineKeyboardButton("➕ Добавить чат", callback_data="add_chat")])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_manage_chats")])
    return InlineKeyboardMarkup(keyboard)

def chat_settings_keyboard(vk_chat_id: str):
    """Клавиатура настроек чата"""
    keyboard = [
        [InlineKeyboardButton("📊 Статистика", callback_data=f"chat_stats_{vk_chat_id}")],
        [InlineKeyboardButton("🔄 Загрузить сообщения", callback_data=f"load_messages_{vk_chat_id}")],
        [InlineKeyboardButton("📋 Проверить суммаризацию", callback_data=f"check_summary_{vk_chat_id}")],
        [InlineKeyboardButton("📤 Вывести в группу", callback_data=f"publish_summary_{vk_chat_id}")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_manage_chats")]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_keyboard():
    """Кнопка 'Назад'"""
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back")]]
    return InlineKeyboardMarkup(keyboard)

def cancel_keyboard():
    """Кнопка 'Отмена'"""
    keyboard = [[InlineKeyboardButton("❌ Отмена", callback_data="cancel")]]
    return InlineKeyboardMarkup(keyboard)

def confirm_keyboard(action: str, data: str = ""):
    """Клавиатура подтверждения"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Да", callback_data=f"confirm_{action}_{data}"),
            InlineKeyboardButton("❌ Нет", callback_data="cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def date_selection_keyboard(dates: list):
    """Клавиатура выбора даты"""
    keyboard = []
    for date in dates:
        keyboard.append([InlineKeyboardButton(
            f"📅 {date['date']} ({date['count']} сообщений)", 
            callback_data=f"select_date_{date['date']}"
        )])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_chat_settings")])
    return InlineKeyboardMarkup(keyboard)

def available_chats_keyboard(chats: list, page: int = 0, per_page: int = 10):
    """Клавиатура выбора доступных чатов VK MAX"""
    keyboard = []
    
    # Вычисляем диапазон для текущей страницы
    start_idx = page * per_page
    end_idx = start_idx + per_page
    page_chats = chats[start_idx:end_idx]
    
    for chat in page_chats:
        # Ограничиваем длину названия чата
        title = chat['title'][:30] + "..." if len(chat['title']) > 30 else chat['title']
        participants = chat['participants_count']
        
        button_text = f"💬 {title} ({participants} чел.)"
        keyboard.append([InlineKeyboardButton(
            button_text,
            callback_data=f"select_available_chat_{chat['id']}"
        )])
    
    # Добавляем навигацию по страницам
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(InlineKeyboardButton("⬅️ Предыдущая", callback_data=f"chats_page_{page-1}"))
    
    if end_idx < len(chats):
        navigation_buttons.append(InlineKeyboardButton("Следующая ➡️", callback_data=f"chats_page_{page+1}"))
    
    if navigation_buttons:
        keyboard.append(navigation_buttons)
    
    # Добавляем кнопки управления
    keyboard.append([InlineKeyboardButton("🔍 Поиск по ID", callback_data="search_chat_by_id")])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_manage_chats")])
    
    return InlineKeyboardMarkup(keyboard)

def chat_add_method_keyboard():
    """Клавиатура выбора способа добавления чата"""
    keyboard = [
        [InlineKeyboardButton("📋 Выбрать из списка", callback_data="select_from_list")],
        [InlineKeyboardButton("🔍 Ввести ID вручную", callback_data="enter_chat_id")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_manage_chats")]
    ]
    return InlineKeyboardMarkup(keyboard)
