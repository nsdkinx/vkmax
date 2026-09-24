"""
Обработчики команд и сообщений для Telegram бота
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from database import DatabaseManager
from vk_integration import VKMaxIntegration
from chat_analyzer import ChatAnalyzer
from keyboards import *

logger = logging.getLogger(__name__)

class BotHandlers:
    """Класс обработчиков для Telegram бота"""
    
    def __init__(self, db_manager: DatabaseManager, vk_integration: VKMaxIntegration, chat_analyzer: ChatAnalyzer):
        self.db = db_manager
        self.vk = vk_integration
        self.analyzer = chat_analyzer
    
    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        chat = update.effective_chat
        
        # Добавляем пользователя в БД
        self.db.add_user(user.id, user.username)
        
        if chat.type == "private":
            # Личные сообщения - показываем выбор группы
            await self._handle_private_start(update, context)
        else:
            # Группа - добавляем в БД и показываем меню
            await self._handle_group_start(update, context)
    
    async def _handle_private_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка /start в личных сообщениях"""
        user = update.effective_user
        
        # Получаем группы пользователя
        user_groups = self.db.get_user_groups(user.id)
        
        if not user_groups:
            await update.message.reply_text(
                "👋 Добро пожаловать!\n\n"
                "Для работы с ботом добавьте его в группу и сделайте администратором."
            )
            return
        
        # Если группа только одна, сразу переходим к управлению чатами
        if len(user_groups) == 1:
            group_id = user_groups[0]['group_id']
            context.user_data['selected_group_id'] = group_id
            
            keyboard = chat_management_keyboard()
            await update.message.reply_text(
                f"👋 Добро пожаловать!\n\n"
                f"✅ Выбрана группа: {user_groups[0]['group_name']}\n\n"
                f"📊 Управление чатами VK MAX",
                reply_markup=keyboard
            )
        else:
            # Показываем выбор группы
            keyboard = group_selection_keyboard(user_groups)
            await update.message.reply_text(
                "👋 Добро пожаловать!\n\n"
                "Выберите группу для работы:",
                reply_markup=keyboard
            )
    
    async def _handle_group_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка /start в группе"""
        chat = update.effective_chat
        user = update.effective_user
        
        # Добавляем группу в БД
        self.db.add_group(chat.id, chat.title)
        
        # Добавляем пользователя в группу как админа
        self.db.add_group_user(chat.id, user.id, is_admin=True)
        
        await update.message.reply_text(
            f"✅ Бот добавлен в группу '{chat.title}'\n\n"
            "Теперь вы можете управлять чатами VK MAX через этого бота."
        )
    
    async def callback_query_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик callback запросов"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "manage_chats":
            await self._handle_manage_chats(update, context)
        elif data == "statistics":
            await self._handle_statistics(update, context)
        elif data == "settings":
            await self._handle_settings(update, context)
        elif data.startswith("select_group_"):
            group_id = int(data.split("_")[2])
            await self._handle_group_selection(update, context, group_id)
        elif data == "add_chat":
            await self._handle_add_chat(update, context)
        elif data == "select_from_list":
            await self._handle_select_from_list(update, context)
        elif data == "enter_chat_id":
            await self._handle_enter_chat_id(update, context)
        elif data.startswith("select_available_chat_"):
            chat_id = data.split("_")[3]
            await self._handle_select_available_chat(update, context, chat_id)
        elif data.startswith("chats_page_"):
            page = int(data.split("_")[2])
            await self._handle_chats_page(update, context, page)
        elif data == "search_chat_by_id":
            await self._handle_search_chat_by_id(update, context)
        elif data.startswith("select_date_"):
            date = data.split("_")[2]
            await self._handle_date_selection(update, context, date)
        elif data == "list_chats":
            await self._handle_list_chats(update, context)
        elif data.startswith("select_chat_"):
            chat_id = data.split("_")[2]
            await self._handle_chat_selection(update, context, chat_id)
        elif data.startswith("chat_stats_"):
            chat_id = data.split("_")[2]
            await self._handle_chat_stats(update, context, chat_id)
        elif data.startswith("load_messages_"):
            chat_id = data.split("_")[2]
            await self._handle_load_messages(update, context, chat_id)
        elif data.startswith("load_new_messages_"):
            chat_id = data.split("_")[3]
            await self._load_messages_worker(update, context, chat_id, load_only_new=True)
        elif data.startswith("load_all_messages_"):
            chat_id = data.split("_")[3]
            await self._load_messages_worker(update, context, chat_id, load_only_new=False)
        elif data.startswith("check_summary_"):
            chat_id = data.split("_")[2]
            await self._handle_check_summary(update, context, chat_id)
        elif data.startswith("publish_summary_"):
            parts = data.split("_")
            if len(parts) == 3:
                # Старый формат без даты
                chat_id = parts[2]
                await self._handle_publish_summary(update, context, chat_id)
            elif len(parts) == 4:
                # Новый формат с датой
                chat_id = parts[2]
                date = parts[3]
                await self._handle_publish_summary_with_date(update, context, chat_id, date)
        elif data == "back_to_main":
            await self._handle_back_to_main(update, context)
        elif data == "change_group":
            await self._handle_change_group(update, context)
        elif data == "back_to_manage_chats":
            await self._handle_back_to_manage_chats(update, context)
        elif data == "back_to_chat_settings":
            chat_id = context.user_data.get('selected_chat_id')
            if chat_id:
                await self._handle_chat_selection(update, context, chat_id)
            else:
                await self._handle_back_to_manage_chats(update, context)
        elif data == "back":
            # Универсальная кнопка "Назад" - возвращаемся к настройкам чата
            chat_id = context.user_data.get('selected_chat_id')
            if chat_id:
                await self._handle_chat_selection(update, context, chat_id)
            else:
                await self._handle_back_to_manage_chats(update, context)
        elif data == "cancel":
            await self._handle_cancel(update, context)
    
    async def _handle_manage_chats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка управления чатами"""
        group_id = context.user_data.get('selected_group_id')
        if not group_id:
            await update.callback_query.edit_message_text(
                "❌ Группа не выбрана",
                reply_markup=back_keyboard()
            )
            return
        
        # Проверяем, есть ли уже чаты в группе
        chats = self.db.get_group_vk_chats(group_id)
        
        if chats:
            # Если чаты есть, сразу показываем их список
            keyboard = chat_list_keyboard(chats)
            await update.callback_query.edit_message_text(
                "📋 Список чатов VK MAX:",
                reply_markup=keyboard
            )
        else:
            # Если чатов нет, показываем меню управления
            keyboard = chat_management_keyboard()
            await update.callback_query.edit_message_text(
                "📊 Управление чатами VK MAX\n\n"
                "Чаты не добавлены. Добавьте первый чат:",
                reply_markup=keyboard
            )
    
    async def _handle_statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка статистики"""
        await update.callback_query.edit_message_text(
            "📈 Статистика\n\n"
            "Функция в разработке...",
            reply_markup=back_keyboard()
        )
    
    async def _handle_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка настроек"""
        await update.callback_query.edit_message_text(
            "🔧 Настройки\n\n"
            "Функция в разработке...",
            reply_markup=back_keyboard()
        )
    
    async def _handle_group_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, group_id: int):
        """Обработка выбора группы"""
        # Сохраняем выбранную группу в контексте
        context.user_data['selected_group_id'] = group_id
        
        # Получаем название группы для отображения
        user_groups = self.db.get_user_groups(update.effective_user.id)
        group_name = "Группа"
        for group in user_groups:
            if group['group_id'] == group_id:
                group_name = group['group_name']
                break
        
        # Проверяем, есть ли уже чаты в группе
        chats = self.db.get_group_vk_chats(group_id)
        
        if chats:
            # Если чаты есть, сразу показываем их список
            keyboard = chat_list_keyboard(chats)
            await update.callback_query.edit_message_text(
                f"✅ Выбрана группа: {group_name}\n\n"
                f"📋 Список чатов VK MAX:",
                reply_markup=keyboard
            )
        else:
            # Если чатов нет, показываем меню управления
            keyboard = chat_management_keyboard()
            await update.callback_query.edit_message_text(
                f"✅ Выбрана группа: {group_name}\n\n"
                f"📊 Управление чатами VK MAX\n\n"
                f"Чаты не добавлены. Добавьте первый чат:",
                reply_markup=keyboard
            )
    
    async def _handle_add_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка добавления чата"""
        keyboard = chat_add_method_keyboard()
        await update.callback_query.edit_message_text(
            "➕ Добавить чат VK MAX\n\n"
            "Выберите способ добавления чата:",
            reply_markup=keyboard
        )
    
    async def _handle_select_from_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка выбора чата из списка"""
        await update.callback_query.edit_message_text(
            "📋 Загружаем список доступных чатов...\n\n"
            "Это может занять несколько секунд.",
            reply_markup=cancel_keyboard()
        )
        
        try:
            # Подключаемся к VK MAX
            if not await self.vk.connect():
                await update.callback_query.edit_message_text(
                    "❌ Ошибка подключения к VK MAX",
                    reply_markup=back_keyboard()
                )
                return
            
            # Получаем список доступных чатов
            available_chats = await self.vk.get_available_chats()
            await self.vk.disconnect()
            
            if not available_chats:
                await update.callback_query.edit_message_text(
                    "❌ Не удалось получить список чатов\n\n"
                    "Попробуйте ввести ID чата вручную.",
                    reply_markup=chat_add_method_keyboard()
                )
                return
            
            # Сохраняем список чатов в контексте
            context.user_data['available_chats'] = available_chats
            context.user_data['chats_page'] = 0
            
            # Показываем первую страницу
            keyboard = available_chats_keyboard(available_chats, 0)
            total_chats = len(available_chats)
            
            await update.callback_query.edit_message_text(
                f"📋 Доступные чаты VK MAX ({total_chats} чатов):\n\n"
                "Выберите чат для добавления:",
                reply_markup=keyboard
            )
            
        except Exception as e:
            logger.error(f"Ошибка получения списка чатов: {e}")
            await update.callback_query.edit_message_text(
                f"❌ Ошибка: {str(e)}",
                reply_markup=chat_add_method_keyboard()
            )
    
    async def _handle_enter_chat_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ввода ID чата вручную"""
        await update.callback_query.edit_message_text(
            "🔍 Ввод ID чата VK MAX\n\n"
            "Введите ID чата VK MAX:",
            reply_markup=cancel_keyboard()
        )
        
        # Устанавливаем состояние ожидания ID чата
        context.user_data['waiting_for_chat_id'] = True
    
    async def _handle_select_available_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: str):
        """Обработка выбора чата из списка"""
        user = update.effective_user
        group_id = context.user_data.get('selected_group_id')
        
        if not group_id:
            await update.callback_query.edit_message_text(
                "❌ Группа не выбрана",
                reply_markup=back_keyboard()
            )
            return
        
        try:
            # Находим информацию о выбранном чате
            available_chats = context.user_data.get('available_chats', [])
            selected_chat = None
            
            for chat in available_chats:
                if str(chat['id']) == str(chat_id):
                    selected_chat = chat
                    break
            
            if not selected_chat:
                await update.callback_query.edit_message_text(
                    "❌ Чат не найден в списке",
                    reply_markup=back_keyboard()
                )
                return
            
            # Добавляем чат в БД
            self.db.add_vk_chat(chat_id, selected_chat['title'], selected_chat['type'])
            self.db.add_group_vk_chat(group_id, chat_id, user.id)
            
            await update.callback_query.edit_message_text(
                f"✅ Чат '{selected_chat['title']}' добавлен\n\n"
                f"👥 Участников: {selected_chat['participants_count']}\n"
                f"🆔 ID: {chat_id}",
                reply_markup=chat_management_keyboard()
            )
            
            # Очищаем данные из контекста
            context.user_data.pop('available_chats', None)
            context.user_data.pop('chats_page', None)
            
        except Exception as e:
            logger.error(f"Ошибка добавления чата: {e}")
            await update.callback_query.edit_message_text(
                f"❌ Ошибка: {str(e)}",
                reply_markup=back_keyboard()
            )
    
    async def _handle_chats_page(self, update: Update, context: ContextTypes.DEFAULT_TYPE, page: int):
        """Обработка переключения страниц списка чатов"""
        available_chats = context.user_data.get('available_chats', [])
        
        if not available_chats:
            await update.callback_query.edit_message_text(
                "❌ Список чатов не найден",
                reply_markup=chat_add_method_keyboard()
            )
            return
        
        # Обновляем номер страницы
        context.user_data['chats_page'] = page
        
        # Показываем страницу
        keyboard = available_chats_keyboard(available_chats, page)
        total_chats = len(available_chats)
        
        await update.callback_query.edit_message_text(
            f"📋 Доступные чаты VK MAX ({total_chats} чатов):\n\n"
            "Выберите чат для добавления:",
            reply_markup=keyboard
        )
    
    async def _handle_search_chat_by_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка поиска чата по ID"""
        await update.callback_query.edit_message_text(
            "🔍 Поиск чата по ID\n\n"
            "Введите ID чата VK MAX:",
            reply_markup=cancel_keyboard()
        )
        
        # Устанавливаем состояние ожидания ID чата
        context.user_data['waiting_for_chat_id'] = True
    
    async def _handle_date_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, date: str):
        """Обработка выбора даты для анализа"""
        chat_id = context.user_data.get('selected_chat_id')
        
        if not chat_id:
            await update.callback_query.edit_message_text(
                "❌ Чат не выбран",
                reply_markup=back_keyboard()
            )
            return
        
        await update.callback_query.edit_message_text(
            f"📊 Анализируем чат за {date}...\n\n"
            "Это может занять некоторое время.",
            reply_markup=cancel_keyboard()
        )
        
        try:
            # Получаем сообщения за выбранную дату
            messages = self.db.get_messages_by_date(chat_id, date)
            
            if not messages:
                await update.callback_query.edit_message_text(
                    f"❌ Нет сообщений за {date}",
                    reply_markup=back_keyboard()
                )
                return
            
            # Анализируем сообщения
            summary = self.analyzer.analyze_chat_by_date(messages)
            
            if summary:
                # Сохраняем суммаризацию в БД
                self.db.save_summary(chat_id, date, summary)
                
                # Показываем результат с Markdown форматированием
                text = f"📊 **Анализ чата за {date}**\n\n"
                text += f"📈 **Статистика:**\n"
                text += f"• Сообщений: {len(messages)}\n"
                text += f"• Дата: {date}\n\n"
                text += f"📝 **Резюме:**\n{summary}"
                
                keyboard = [
                    [InlineKeyboardButton("📤 Вывести в группу", callback_data=f"publish_summary_{chat_id}_{date}")],
                    [InlineKeyboardButton("🔙 Назад", callback_data=f"select_chat_{chat_id}")]
                ]
                
                await update.callback_query.edit_message_text(
                    text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update.callback_query.edit_message_text(
                    f"❌ Не удалось проанализировать чат за {date}\n\n"
                    "Попробуйте другую дату или проверьте настройки GigaChat.",
                    reply_markup=back_keyboard()
                )
                
        except Exception as e:
            logger.error(f"Ошибка анализа чата: {e}")
            await update.callback_query.edit_message_text(
                f"❌ Ошибка анализа: {str(e)}",
                reply_markup=back_keyboard()
            )
    
    async def _handle_list_chats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка списка чатов"""
        group_id = context.user_data.get('selected_group_id')
        if not group_id:
            await update.callback_query.edit_message_text(
                "❌ Группа не выбрана",
                reply_markup=back_keyboard()
            )
            return
        
        chats = self.db.get_group_vk_chats(group_id)
        
        if not chats:
            await update.callback_query.edit_message_text(
                "📋 Список чатов пуст\n\n"
                "Добавьте чат с помощью кнопки '➕ Добавить чат'",
                reply_markup=chat_management_keyboard()
            )
            return
        
        keyboard = chat_list_keyboard(chats)
        await update.callback_query.edit_message_text(
            "📋 Список чатов VK MAX:",
            reply_markup=keyboard
        )
    
    async def _handle_chat_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: str):
        """Обработка выбора чата"""
        context.user_data['selected_chat_id'] = chat_id
        
        # Получаем статистику чата
        stats = self.db.get_chat_stats(chat_id)
        
        text = f"💬 Чат: {chat_id}\n\n"
        text += f"📊 Статистика:\n"
        text += f"• Всего сообщений: {stats['total_messages']}\n"
        text += f"• Дней загружено: {stats['days_count']}\n\n"
        
        if stats['recent_days']:
            text += "📅 Последние дни:\n"
            for day in stats['recent_days'][:5]:
                text += f"• {day['date']} ({day['count']} сообщений)\n"
        
        keyboard = chat_settings_keyboard(chat_id)
        await update.callback_query.edit_message_text(
            text,
            reply_markup=keyboard
        )
    
    async def _handle_chat_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: str):
        """Обработка статистики чата"""
        stats = self.db.get_chat_stats(chat_id)
        
        text = f"📊 Статистика чата {chat_id}\n\n"
        text += f"• Всего сообщений: {stats['total_messages']}\n"
        text += f"• Дней загружено: {stats['days_count']}\n\n"
        
        if stats['recent_days']:
            text += "📅 Последние дни:\n"
            for day in stats['recent_days']:
                text += f"• {day['date']} ({day['count']} сообщений)\n"
        
        await update.callback_query.edit_message_text(
            text,
            reply_markup=back_keyboard()
        )
    
    async def _handle_load_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: str):
        """Обработка загрузки сообщений"""
        # Проверяем, есть ли уже сообщения в чате
        last_timestamp = self.db.get_last_message_timestamp(chat_id)
        
        if last_timestamp:
            # Если сообщения уже есть, предлагаем загрузить только новые
            keyboard = [
                [InlineKeyboardButton("🔄 Загрузить только новые", callback_data=f"load_new_messages_{chat_id}")],
                [InlineKeyboardButton("🔄 Загрузить все заново", callback_data=f"load_all_messages_{chat_id}")],
                [InlineKeyboardButton("🔙 Назад", callback_data=f"select_chat_{chat_id}")]
            ]
            
            await update.callback_query.edit_message_text(
                f"📊 В чате уже есть сообщения\n\n"
                f"Последнее сообщение: {datetime.fromtimestamp(last_timestamp/1000).strftime('%Y-%m-%d %H:%M')}\n\n"
                f"Выберите тип загрузки:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            # Если сообщений нет, загружаем все
            await self._load_messages_worker(update, context, chat_id, load_only_new=False)
    
    async def _load_messages_worker(self, update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: str, load_only_new: bool = False):
        """Рабочий метод загрузки сообщений"""
        await update.callback_query.edit_message_text(
            f"🔄 {'Загружаем новые сообщения' if load_only_new else 'Загружаем сообщения'}...\n\n"
            "Это может занять некоторое время.",
            reply_markup=cancel_keyboard()
        )
        
        try:
            # Подключаемся к VK MAX
            if not await self.vk.connect():
                await update.callback_query.edit_message_text(
                    "❌ Ошибка подключения к VK MAX",
                    reply_markup=back_keyboard()
                )
                return
            
            # Загружаем сообщения
            messages = await self.vk.load_chat_messages(chat_id, db_manager=self.db, load_only_new=load_only_new)
            
            if not messages:
                await update.callback_query.edit_message_text(
                    f"❌ {'Нет новых сообщений' if load_only_new else 'Не удалось загрузить сообщения'}",
                    reply_markup=back_keyboard()
                )
                return
            
            # Сохраняем в БД
            await self.vk.save_messages_to_db(self.db, chat_id, messages)
            
            message_type = "новых" if load_only_new else ""
            await update.callback_query.edit_message_text(
                f"✅ Загружено {len(messages)} {message_type} сообщений",
                reply_markup=back_keyboard()
            )
            
        except Exception as e:
            logger.error(f"Ошибка загрузки сообщений: {e}")
            await update.callback_query.edit_message_text(
                f"❌ Ошибка: {str(e)}",
                reply_markup=back_keyboard()
            )
        finally:
            await self.vk.disconnect()
    
    async def _handle_check_summary(self, update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: str):
        """Обработка проверки суммаризации"""
        # Получаем последние дни
        stats = self.db.get_chat_stats(chat_id)
        
        if not stats['recent_days']:
            await update.callback_query.edit_message_text(
                "❌ Нет данных для анализа",
                reply_markup=back_keyboard()
            )
            return
        
        # Показываем выбор даты
        keyboard = date_selection_keyboard(stats['recent_days'])
        await update.callback_query.edit_message_text(
            "📋 Выберите дату для анализа:",
            reply_markup=keyboard
        )
    
    async def _handle_publish_summary(self, update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: str):
        """Обработка публикации суммаризации (выбор из доступных)"""
        # Получаем список доступных суммаризаций
        summaries = self.db.get_available_summaries(chat_id)
        
        if not summaries:
            await update.callback_query.edit_message_text(
                f"📤 Публикация суммаризации\n\n"
                f"❌ Нет доступных суммаризаций для чата {chat_id}\n\n"
                f"Сначала создайте суммаризацию через '📋 Проверить суммаризацию'",
                reply_markup=back_keyboard()
            )
            return
        
        # Показываем список доступных суммаризаций
        keyboard = []
        for summary in summaries:
            date = summary['date']
            keyboard.append([InlineKeyboardButton(
                f"📅 {date}", 
                callback_data=f"publish_summary_{chat_id}_{date}"
            )])
        
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data=f"select_chat_{chat_id}")])
        
        text = f"📤 **Публикация суммаризации**\n\n"
        text += f"📊 Доступные суммаризации для чата {chat_id}:\n\n"
        text += f"Выберите дату для публикации:"
        
        await update.callback_query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def _handle_publish_summary_with_date(self, update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: str, date: str):
        """Обработка публикации суммаризации с датой"""
        group_id = context.user_data.get('selected_group_id')
        
        if not group_id:
            await update.callback_query.edit_message_text(
                "❌ Группа не выбрана",
                reply_markup=back_keyboard()
            )
            return
        
        try:
            # Получаем суммаризацию из БД
            summary = self.db.get_summary(chat_id, date)
            
            if not summary:
                await update.callback_query.edit_message_text(
                    f"❌ Суммаризация за {date} не найдена\n\n"
                    "Сначала создайте суммаризацию для этой даты.",
                    reply_markup=back_keyboard()
                )
                return
            
            # Получаем название чата из БД
            chat_info = self.db.get_vk_chat_info(chat_id)
            chat_name = chat_info.get('chat_name', f'Чат {chat_id}') if chat_info else f'Чат {chat_id}'
            
            # Форматируем сообщение для публикации
            from telegram_bot.utils import format_summary_for_telegram
            
            # Разбиваем на части если нужно
            message_parts = format_summary_for_telegram(summary, date, chat_name)
            
            # Отправляем в группу
            await update.callback_query.edit_message_text(
                f"📤 Публикуем суммаризацию в группу...\n\n"
                f"Чат: {chat_id}\n"
                f"Дата: {date}",
                reply_markup=cancel_keyboard()
            )
            
            # Проверяем, есть ли уже опубликованные сообщения для этой даты
            existing_message_ids = []
            for i in range(len(message_parts)):
                message_id = self.db.get_group_message(group_id, chat_id, f"{date}_{i}")
                if message_id:
                    existing_message_ids.append(message_id)
                else:
                    existing_message_ids.append(None)
            
            # Отправляем или обновляем сообщения в группе
            sent_message_ids = []
            for i, part in enumerate(message_parts):
                try:
                    if existing_message_ids[i]:
                        # Обновляем существующее сообщение
                        await context.bot.edit_message_text(
                            chat_id=group_id,
                            message_id=existing_message_ids[i],
                            text=part,
                            parse_mode=ParseMode.MARKDOWN_V2
                        )
                        sent_message_ids.append(existing_message_ids[i])
                        logger.info(f"✅ Обновлено сообщение {i+1} (ID: {existing_message_ids[i]})")
                    else:
                        # Отправляем новое сообщение
                        message = await context.bot.send_message(
                            chat_id=group_id,
                            text=part,
                            parse_mode=ParseMode.MARKDOWN_V2,
                            disable_notification=True
                        )
                        sent_message_ids.append(message.message_id)
                        logger.info(f"✅ Отправлено новое сообщение {i+1} (ID: {message.message_id})")
                    
                    if i < len(message_parts) - 1:
                        await asyncio.sleep(0.5)  # Пауза между сообщениями
                except Exception as e:
                    logger.error(f"Ошибка обработки сообщения {i+1}: {e}")
                    break
            
            # Сохраняем message_id в БД для каждой части
            for i, message_id in enumerate(sent_message_ids):
                if message_id:
                    self.db.update_group_message(group_id, chat_id, f"{date}_{i}", message_id)
            
            # Подсчитываем статистику
            updated_count = sum(1 for msg_id in existing_message_ids if msg_id is not None)
            new_count = len(sent_message_ids) - updated_count
            
            await update.callback_query.edit_message_text(
                f"✅ Суммаризация опубликована в группу!\n\n"
                f"📊 Чат: {chat_id}\n"
                f"📅 Дата: {date}\n"
                f"📝 Частей: {len(message_parts)}\n"
                f"🔄 Обновлено: {updated_count}\n"
                f"➕ Новых: {new_count}",
                reply_markup=back_keyboard()
            )
            
        except Exception as e:
            logger.error(f"Ошибка публикации суммаризации: {e}")
            await update.callback_query.edit_message_text(
                f"❌ Ошибка публикации: {str(e)}",
                reply_markup=back_keyboard()
            )
    
    async def _handle_back_to_main(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка возврата в главное меню"""
        keyboard = main_menu_keyboard()
        await update.callback_query.edit_message_text(
            "🏠 Главное меню\n\n"
            "Выберите действие:",
            reply_markup=keyboard
        )
    
    async def _handle_change_group(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка смены группы"""
        # Получаем все группы, где есть бот
        all_groups = self.db.get_all_groups()
        
        if not all_groups:
            await update.callback_query.edit_message_text(
                "❌ Нет доступных групп\n\n"
                "Для работы с ботом добавьте его в группу и сделайте администратором.",
                reply_markup=back_keyboard()
            )
            return
        
        # Показываем выбор группы
        keyboard = group_selection_keyboard(all_groups)
        await update.callback_query.edit_message_text(
            "🔄 Смена группы\n\n"
            "Выберите группу для работы:",
            reply_markup=keyboard
        )
    
    async def _handle_back_to_manage_chats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка возврата к управлению чатами"""
        group_id = context.user_data.get('selected_group_id')
        if not group_id:
            await update.callback_query.edit_message_text(
                "❌ Группа не выбрана",
                reply_markup=back_keyboard()
            )
            return
        
        # Проверяем, есть ли уже чаты в группе
        chats = self.db.get_group_vk_chats(group_id)
        
        if chats:
            # Если чаты есть, сразу показываем их список
            keyboard = chat_list_keyboard(chats)
            await update.callback_query.edit_message_text(
                "📋 Список чатов VK MAX:",
                reply_markup=keyboard
            )
        else:
            # Если чатов нет, показываем меню управления
            keyboard = chat_management_keyboard()
            await update.callback_query.edit_message_text(
                "📊 Управление чатами VK MAX\n\n"
                "Чаты не добавлены. Добавьте первый чат:",
                reply_markup=keyboard
            )
    
    async def _handle_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка отмены"""
        # Очищаем состояние
        context.user_data.pop('waiting_for_chat_id', None)
        context.user_data.pop('selected_chat_id', None)
        context.user_data.pop('available_chats', None)
        context.user_data.pop('chats_page', None)
        
        keyboard = main_menu_keyboard()
        await update.callback_query.edit_message_text(
            "❌ Операция отменена\n\n"
            "Выберите действие:",
            reply_markup=keyboard
        )
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        if context.user_data.get('waiting_for_chat_id'):
            await self._handle_chat_id_input(update, context)
        else:
            await update.message.reply_text(
                "Используйте кнопки для навигации или команду /start"
            )
    
    async def _handle_chat_id_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ввода ID чата"""
        chat_id = update.message.text.strip()
        user = update.effective_user
        group_id = context.user_data.get('selected_group_id')
        
        if not group_id:
            await update.message.reply_text(
                "❌ Группа не выбрана",
                reply_markup=back_keyboard()
            )
            return
        
        try:
            # Проверяем доступ к чату
            if not await self.vk.connect():
                await update.message.reply_text(
                    "❌ Ошибка подключения к VK MAX",
                    reply_markup=back_keyboard()
                )
                return
            
            chat_info = await self.vk.get_chat_info(chat_id)
            await self.vk.disconnect()
            
            if not chat_info:
                await update.message.reply_text(
                    f"❌ Чат {chat_id} не найден или недоступен",
                    reply_markup=back_keyboard()
                )
                return
            
            # Добавляем чат в БД
            self.db.add_vk_chat(chat_id, chat_info['title'], chat_info['type'])
            self.db.add_group_vk_chat(group_id, chat_id, user.id)
            
            await update.message.reply_text(
                f"✅ Чат '{chat_info['title']}' добавлен",
                reply_markup=chat_management_keyboard()
            )
            
        except Exception as e:
            logger.error(f"Ошибка добавления чата: {e}")
            await update.message.reply_text(
                f"❌ Ошибка: {str(e)}",
                reply_markup=back_keyboard()
            )
        finally:
            # Очищаем состояние
            context.user_data.pop('waiting_for_chat_id', None)
