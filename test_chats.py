import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime

from vkmax.client import MaxClient
from vkmax.functions.chats import (
    get_chats,
    get_chat_messages,
    mark_chat_as_read,
    mark_chat_as_unread,
    mute_chat,
    leave_chat,
    join_chat,
)
from vkmax.functions.messages import send_message

# Настройка логирования
logging.basicConfig(
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


async def test_mark_as_read(client, chat_id):
    """Тест: пометить чат как прочитанный"""
    try:
        # Получаем последнее сообщение
        messages_response = await get_chat_messages(client, chat_id, count=1)
        if (
            "payload" in messages_response
            and "messages" in messages_response["payload"]
        ):
            messages = messages_response["payload"]["messages"]
            if messages:
                msg_id = messages[0].get("id")
                logger.info(
                    f"Помечаю последнее сообщение ({msg_id}) как прочитанное..."
                )
                response = await mark_chat_as_read(client, chat_id, msg_id)
                logger.info(f"✅ Результат: {response.get('opcode', 'OK')}")
                return True
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
    return False


async def test_mark_as_unread(client, chat_id):
    """Тест: пометить чат как непрочитанный"""
    try:
        logger.info("Помечаю чат как непрочитанный...")
        response = await mark_chat_as_unread(client, chat_id)
        logger.info(f"✅ Результат: {response.get('opcode', 'OK')}")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return False


async def load_last_week_messages(client, chat_id):
    """Загрузить сообщения за последнюю неделю"""
    from datetime import timedelta

    print("\n" + "=" * 70)
    logger.info("📊 Загрузка сообщений за последнюю неделю...")
    print("=" * 70)

    # Текущее время
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    week_ago_timestamp = int(week_ago.timestamp() * 1000)

    print(
        f"📅 Период: {week_ago.strftime('%d.%m.%Y %H:%M')} - {now.strftime('%d.%m.%Y %H:%M')}"
    )
    print(f"⏰ Timestamp недели назад: {week_ago_timestamp}")
    print(f"⏰ Текущий timestamp: {int(now.timestamp() * 1000)}")
    print()

    all_messages = []
    seen_message_ids = set()  # Для фильтрации дубликатов
    last_msg_timestamp = (
        None  # Используем timestamp для пагинации (API ожидает timestamp, а не ID)
    )
    batch_size = 100  # API максимум 100 за раз
    batch_count = 0
    duplicates_skipped = 0  # Счетчик дубликатов

    try:
        while True:
            batch_count += 1

            # Загружаем порцию сообщений
            # Используем timestamp самого старого сообщения для следующей итерации
            response = await get_chat_messages(
                client, chat_id, count=batch_size, from_message_id=last_msg_timestamp
            )

            if "payload" not in response or "messages" not in response["payload"]:
                logger.warning("⚠️  Нет данных в ответе")
                break

            messages = response["payload"]["messages"]
            if not messages:
                logger.info("📭 Больше нет сообщений в чате")
                break

            # Фильтруем сообщения по времени и дубликатам
            messages_in_range = 0
            has_old_messages = False
            batch_duplicates = 0

            for msg in messages:
                msg_time = msg.get("time", 0)
                msg_id = msg.get("id") or msg.get("messageId")

                # Проверяем на дубликат (API может возвращать дубликаты при пагинации по timestamp)
                if msg_id and msg_id in seen_message_ids:
                    batch_duplicates += 1
                    continue

                # Если сообщение старше недели
                if msg_time < week_ago_timestamp:
                    has_old_messages = True
                    continue  # Пропускаем старое сообщение, но продолжаем проверять остальные

                # Сообщение в пределах недели - добавляем
                if msg_id:
                    seen_message_ids.add(msg_id)
                all_messages.append(msg)
                messages_in_range += 1

            duplicates_skipped += batch_duplicates

            # Показываем прогресс
            if messages:
                # API возвращает сообщения от СТАРЫХ к НОВЫМ (ascending)
                # messages[0] = самое старое, messages[-1] = самое новое
                oldest_time = messages[0].get("time", 0)
                newest_time = messages[-1].get("time", 0)
                oldest_id = messages[0].get("id") or messages[0].get("messageId")
                newest_id = messages[-1].get("id") or messages[-1].get("messageId")
                oldest_in_batch = datetime.fromtimestamp(oldest_time / 1000)
                newest_in_batch = datetime.fromtimestamp(newest_time / 1000)
                dup_info = (
                    f" | дубликатов: {batch_duplicates}" if batch_duplicates > 0 else ""
                )
                print(
                    f"📥 Пакет {batch_count}: +{messages_in_range} в периоде из {len(messages)} загруженных{dup_info} | Всего за неделю: {len(all_messages)}",
                    flush=True,
                )
                print(
                    f"   Диапазон времени: {newest_in_batch.strftime('%d.%m %H:%M')} -> {oldest_in_batch.strftime('%d.%m %H:%M')}",
                    flush=True,
                )
                print(
                    f"   Диапазон ID: {newest_id} -> {oldest_id} | old_msgs: {has_old_messages}",
                    flush=True,
                )
                if batch_count > 1 and last_msg_timestamp:
                    print(
                        f"   Использован from_timestamp: {last_msg_timestamp}",
                        flush=True,
                    )

            # Если все сообщения в порции старые - останавливаемся
            if messages_in_range == 0 and has_old_messages:
                logger.info(
                    f"✅ Достигнут конец периода (все {len(messages)} сообщений в пакете старше недели)"
                )
                break

            # Если загрузили меньше чем batch_size, значит достигли конца чата
            if len(messages) < batch_size:
                logger.info(
                    f"📭 Достигнут конец чата (загружено {len(messages)} < {batch_size})"
                )
                break

            # Получаем timestamp самого старого сообщения для следующей итерации
            # API использует timestamp в поле 'from', а не ID сообщения
            # API возвращает messages от старых к новым, поэтому берем messages[0]
            last_message = messages[0]
            last_msg_timestamp = last_message.get("time", 0)

            if not last_msg_timestamp:
                logger.error("Не удалось получить timestamp последнего сообщения")
                break

            # Вычитаем 1 мс чтобы не получить то же сообщение снова
            last_msg_timestamp = last_msg_timestamp - 1

            # Защита от бесконечного цикла
            if len(all_messages) > 10000:
                logger.warning("\n⚠️  Достигнут лимит в 10000 сообщений")
                break

            await asyncio.sleep(0.3)  # Пауза между запросами

        # Если дошли до конца чата
        print()  # Новая строка после прогресса
        logger.info(
            f"✅ Загружено {len(all_messages)} уникальных сообщений за доступный период"
        )
        if duplicates_skipped > 0:
            logger.info(f"🔄 Пропущено {duplicates_skipped} дубликатов при пагинации")
        show_week_statistics(all_messages, week_ago, now)
        show_recent_messages(all_messages)
        return all_messages

    except Exception as e:
        print()  # Новая строка после прогресса
        logger.error(f"❌ Ошибка при загрузке: {e}")
        if all_messages:
            logger.info(f"Частично загружено: {len(all_messages)} уникальных сообщений")
            if duplicates_skipped > 0:
                logger.info(
                    f"🔄 Пропущено {duplicates_skipped} дубликатов при пагинации"
                )
            show_week_statistics(all_messages, week_ago, now)
            show_recent_messages(all_messages)
        return all_messages


def show_week_statistics(messages, week_ago, now):
    """Показать статистику за неделю"""
    if not messages:
        print("\n⚠️  Нет сообщений за последнюю неделю")
        return

    print("\n" + "=" * 70)
    print("📊 СТАТИСТИКА ЗА ПОСЛЕДНЮЮ НЕДЕЛЮ")
    print("=" * 70)
    print(f"\n📨 Всего сообщений: {len(messages)}")

    # Группируем по дням
    days_stats = {}
    sender_stats = {}
    hour_stats = {}

    for msg in messages:
        msg_time = msg.get("time", 0)
        if msg_time:
            dt = datetime.fromtimestamp(msg_time / 1000)
            day_key = dt.strftime("%Y-%m-%d")
            hour_key = dt.hour

            # Статистика по дням
            if day_key not in days_stats:
                days_stats[day_key] = 0
            days_stats[day_key] += 1

            # Статистика по часам
            if hour_key not in hour_stats:
                hour_stats[hour_key] = 0
            hour_stats[hour_key] += 1

            # Статистика по отправителям
            sender_id = msg.get("sender", "Unknown")
            if sender_id not in sender_stats:
                sender_stats[sender_id] = 0
            sender_stats[sender_id] += 1

    # Показываем статистику по дням
    print("\n📅 Сообщений по дням:")
    max_count = max(days_stats.values()) if days_stats else 1
    for day in sorted(days_stats.keys(), reverse=True):
        dt = datetime.strptime(day, "%Y-%m-%d")
        # Формат: день.месяц.год (день_недели)
        day_name = dt.strftime("%d.%m.%Y (%A)")
        # Проверка на правильность года
        if dt.year > 2025:
            logger.warning(f"⚠️  Странная дата: {day_name}, timestamp проблема?")
        count = days_stats[day]
        bar_length = int((count / max_count) * 40)
        bar = "█" * bar_length
        print(f"  {day_name}: {count:4d} {bar}")

    # Показываем топ-5 активных пользователей
    print("\n👥 Топ-5 активных участников:")
    sorted_senders = sorted(sender_stats.items(), key=lambda x: x[1], reverse=True)
    for idx, (sender_id, count) in enumerate(sorted_senders[:5], 1):
        percentage = (count / len(messages)) * 100
        print(f"  {idx}. User {sender_id}: {count} сообщений ({percentage:.1f}%)")

    # Самые активные часы
    print("\n🕐 Топ-5 самых активных часов:")
    sorted_hours = sorted(hour_stats.items(), key=lambda x: x[1], reverse=True)
    for hour, count in sorted_hours[:5]:
        print(f"  {hour:02d}:00 - {count} сообщений")

    # Средняя активность
    avg_per_day = len(messages) / 7
    print(f"\n📈 Среднее сообщений в день: {avg_per_day:.1f}")

    print("=" * 70)


def show_recent_messages(messages, count=10):
    """Показать последние N сообщений"""
    if not messages:
        return

    print("\n" + "=" * 70)
    print(f"💬 ПОСЛЕДНИЕ {min(count, len(messages))} СООБЩЕНИЙ:")
    print("=" * 70 + "\n")

    recent = sorted(messages, key=lambda x: x.get("time", 0), reverse=True)[:count]

    for idx, msg in enumerate(reversed(recent), 1):
        text = msg.get("text", "")
        sender = msg.get("sender")
        timestamp = msg.get("time", 0)

        if timestamp:
            dt = datetime.fromtimestamp(timestamp / 1000)
            time_str = dt.strftime("%d.%m %H:%M")
        else:
            time_str = "??:??:??"

        preview = text[:70] + "..." if len(text) > 70 else text
        print(f"{idx:2d}. [{time_str}] User {sender}: {preview}")

    print("=" * 70)


async def test_mute_chat(client, chat_id, mute: bool):
    """Тест: выключить/включить уведомления"""
    try:
        action = "Выключаю" if mute else "Включаю"
        logger.info(f"{action} уведомления для чата...")
        response = await mute_chat(client, chat_id, forever=mute)
        logger.info(f"✅ Результат: {response.get('opcode', 'OK')}")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return False


async def test_send_message(client, chat_id):
    """Тест: отправить сообщение"""
    try:
        test_text = input("Введите текст сообщения для отправки: ").strip()
        if not test_text:
            test_text = "🧪 Тестовое сообщение из vkmax"

        logger.info(f"Отправляю сообщение: {test_text}")
        response = await send_message(client, chat_id, test_text)
        logger.info(
            f"✅ Сообщение отправлено! ID: {response.get('payload', {}).get('message', {}).get('id', '?')}"
        )
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return False


async def test_join_chat(client):
    """Тест: вступить в чат по ссылке"""
    try:
        link = input(
            "Введите ссылку на чат/канал (например, https://max.ru/gosuslugi): "
        ).strip()
        if not link:
            logger.warning("Ссылка не введена")
            return False

        logger.info(f"Пытаюсь вступить в чат по ссылке: {link}")
        response = await join_chat(client, link)
        logger.info(f"✅ Результат: {response}")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return False


async def show_test_menu(client, chat_id, chat_name):
    """Показать меню тестирования функций"""
    while True:
        print("\n" + "=" * 70)
        print(f"🧪 ТЕСТИРОВАНИЕ ФУНКЦИЙ ДЛЯ ЧАТА: {chat_name}")
        print(f"   Chat ID: {chat_id}")
        print("=" * 70)
        print("\n1. 📊 Статистика за неделю + все сообщения (load_last_week_messages)")
        print("2. ✅ Пометить как прочитанный (mark_chat_as_read)")
        print("3. ⭕ Пометить как непрочитанный (mark_chat_as_unread)")
        print("4. 🔕 Выключить уведомления (mute_chat)")
        print("5. 🔔 Включить уведомления (unmute_chat)")
        print("6. 📤 Отправить сообщение (send_message)")
        print("7. 🔙 Вернуться к списку чатов")
        print("8. 🚪 Выход")
        print("=" * 70)

        choice = input("\nВыберите действие (1-8): ").strip()

        if choice == "1":
            # Статистика за неделю - загружаем все сообщения автоматически
            await load_last_week_messages(client, chat_id)

        elif choice == "2":
            await test_mark_as_read(client, chat_id)

        elif choice == "3":
            await test_mark_as_unread(client, chat_id)

        elif choice == "4":
            await test_mute_chat(client, chat_id, mute=True)

        elif choice == "5":
            await test_mute_chat(client, chat_id, mute=False)

        elif choice == "6":
            await test_send_message(client, chat_id)

        elif choice == "7":
            break

        elif choice == "8":
            return True  # Выход из программы

        else:
            logger.warning("Неверный выбор")

        input("\nНажмите Enter для продолжения...")

    return False  # Вернуться к списку чатов


async def main():
    """
    Тестовый скрипт для работы с чатами VK MAX.

    1. Авторизуется по токену
    2. Получает список чатов
    3. Позволяет выбрать чат
    4. Показывает меню тестирования всех функций из chats.py
    """

    client = MaxClient()

    try:
        # Подключение
        logger.info("🔌 Подключение к VK MAX...")
        await client.connect()

        # Авторизация
        login_token_file = Path("login_token.txt")

        if not login_token_file.exists():
            logger.error("❌ Файл login_token.txt не найден!")
            logger.info("Создайте файл login_token.txt и поместите в него ваш токен")
            return

        token = login_token_file.read_text(encoding="utf-8").strip()

        logger.info("🔑 Авторизация...")
        await client.login_by_token(token)
        logger.info("✅ Авторизация успешна!\n")

        # Получение списка чатов (синхронно, из кеша)
        logger.info("📋 Получение списка чатов...")
        response = get_chats(client)

        if "payload" not in response or "chats" not in response["payload"]:
            logger.error("❌ Не удалось получить список чатов")
            return

        chats = response["payload"]["chats"]

        logger.info(f"📊 Всего получено чатов: {len(chats)}")

        # Отладка: показываем все чаты
        logger.info("🔍 Анализ полученных чатов:")
        for idx, chat in enumerate(chats, 1):
            chat_id = chat.get("id", 0)  # В API используется 'id', а не 'chatId'
            chat_type = chat.get("type", "")
            has_bots = chat.get("hasBots", False)
            restrictions = chat.get("restrictions", 0)
            title = chat.get("title", "?")
            logger.info(
                f"  {idx}. ID={chat_id}, type={chat_type}, hasBots={has_bots}, "
                f"restrictions={restrictions}, title={title}"
            )

        # Фильтруем чаты (убираем только Избранное с id=0 и служебные с restrictions=64)
        real_chats = []
        for chat in chats:
            chat_id = chat.get("id", 0)  # В API используется 'id', а не 'chatId'
            chat_type = chat.get("type", "")
            restrictions = chat.get("restrictions", 0)

            # Пропускаем Избранное (id=0) и служебные чаты (restrictions=64)
            if chat_id == 0 or restrictions == 64:
                continue

            real_chats.append(chat)

        logger.info(f"✅ После фильтрации: {len(real_chats)} чатов")

        if not real_chats:
            logger.warning("⚠️  Не найдено чатов после фильтрации")
            return

        # Главный цикл - показываем чаты и позволяем выбирать действия
        while True:
            # Выводим список чатов
            print("\n" + "=" * 70)
            print("💬 СПИСОК ЧАТОВ:")
            print("=" * 70 + "\n")

            for idx, chat in enumerate(real_chats, 1):
                chat_id = chat.get("id")  # В API используется 'id', а не 'chatId'
                chat_type = chat.get("type", "UNKNOWN")

                # Определяем название
                if "title" in chat:
                    name = chat["title"]
                elif "member" in chat:
                    member = chat["member"]
                    if "names" in member and member["names"]:
                        name = member["names"][0].get("name", f"Chat {chat_id}")
                    else:
                        name = f"Chat {chat_id}"
                else:
                    name = f"Chat {chat_id}"

                # Непрочитанные сообщения
                unread = chat.get("newMessages", 0)

                # Иконка типа чата
                type_icon = {
                    "DIALOG": "👤",
                    "CHAT": "👥",
                    "CHANNEL": "📢",
                }.get(chat_type, "💭")

                # Количество участников
                participants_count = chat.get("participantsCount", 0)
                participants_str = ""
                if participants_count > 0:
                    participants_str = f" ({participants_count} участников)"

                # Непрочитанные
                unread_str = ""
                if unread > 0:
                    unread_str = f" 🔴 {unread} непрочитанных"

                print(f"{idx}. {type_icon} {name}{participants_str}{unread_str}")
                print(f"   ID: {chat_id}, Тип: {chat_type}")

                # Последнее сообщение
                if "lastMessage" in chat:
                    last_msg = chat["lastMessage"]
                    text = last_msg.get("text", "")
                    if text:
                        preview = text[:50]
                        if len(text) > 50:
                            preview += "..."
                        print(f"   Последнее: {preview}")

                print()

            # Выбор чата
            print("=" * 70)
            choice = input(
                f"\nВыберите чат (1-{len(real_chats)}) | 0 - доп.функции | Enter - выход: "
            ).strip()

            # Главное меню: выбор чата или тест join_chat
            if not choice:
                print("\n" + "=" * 70)
                print("ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ:")
                print("=" * 70)
                print("\n1. 🔗 Вступить в чат по ссылке (join_chat)")
                print("0. Выход")

                extra = input("\nВыберите действие: ").strip()
                if extra == "1":
                    await test_join_chat(client)
                    input("\nНажмите Enter для продолжения...")
                    continue
                else:
                    logger.info("👋 Выход")
                    return

            if not choice.isdigit():
                logger.error("❌ Некорректный ввод")
                continue

            chat_idx = int(choice) - 1

            if chat_idx < 0 or chat_idx >= len(real_chats):
                logger.error("❌ Неверный номер чата")
                continue

            # Получаем выбранный чат
            selected_chat = real_chats[chat_idx]
            chat_id = selected_chat.get("id")

            if "title" in selected_chat:
                chat_name = selected_chat["title"]
            else:
                chat_name = f"Chat {chat_id}"

            # Показываем меню тестирования функций
            should_exit = await show_test_menu(client, chat_id, chat_name)
            if should_exit:
                logger.info("👋 Выход")
                return

    except Exception as e:
        logger.error(f"\n❌ Ошибка: {e}", exc_info=True)

    finally:
        await client.disconnect()
        logger.info("👋 Отключено от сервера")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Прервано пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)
