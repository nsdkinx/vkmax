from Maxon.init import VERSION, START_TIME
from pathlib import Path
from json import load, dump

__name__ = "Реквизиты"
__description__ = "Сохраняет и отправляет Ваши реквизиты в удобном формате"
__version__ = "1.1.0"
__author__ = "@nerkux"

REKV = "userdata//rekv.json"

def load_data():
    with open(REKV, 'r', encoding='utf-8') as f:
        return load(f)

def save_data(data):
    with open(REKV, 'w', encoding='utf-8') as f:
        dump(data, f, ensure_ascii=False, indent=2)

def add_rekv(name, value):
    data = load_data()
    next_id = 1 if not data else max(item['id'] for item in data) + 1
    data.append({'id': next_id, 'name': name, 'value': value})
    save_data(data)
    return f"✅ Реквизит добавлен\n\nID: {next_id}\nНазвание: {name}\nЗначение: {value}"

def remove_rekv(identifier):
    if identifier == "0":
        return "⚠️ Реквизиты не найдены"
    data = load_data()
    try:
        identifier = int(identifier)
        new_data = [item for item in data if item['id'] != identifier]
    except ValueError:
        new_data = [item for item in data if item['name'] != identifier]

    if len(new_data) == len(data):
        return "⚠️ Реквизиты не найдены"
    else:

        for i, item in enumerate(new_data):
            item['id'] = i

        save_data(new_data)
        return "🗑️ Реквизиты успешно удалены"

def list_rekv():
    data = load_data()
    if not data:
        return "📭 Список реквизитов пуст"
    
    lines = []
    for item in data:
        if item['id'] != 0:
            lines.append(f"{item['id']}. {item['name']}\n{item['value']}")
    return "\n\n".join(lines)


async def handle(packet, args):

    if args == []:
        data = load_data()
        if len(data) == 1:
            return "Для добавления реквизитов используйте \n.rekv add [название] [значение]"
        else:
            return list_rekv()
    
    if len(args) == 3:
        if args[0] == "add" and args[1] and args[2]:
            if Path(REKV).exists():
                return add_rekv(args[1], args[2])
            
            else:
                with open(REKV, 'w', encoding='utf-8') as f:
                    f.close()
                return add_rekv(args[1], args[2])

        if args[0] == "add" and not args[1] or not args[2]:
            return "Для добавления реквизитов используйте \n.rekv add [название] [значение]"
    if len(args) == 2:
        if args[0] == "remove" and args[1]:
            return remove_rekv(args[1])
        
        if args[0] == "remove" and not args[1]:
            return "Для удаления реквизитов используйте \n.rekv remove [номер | название]"
    
    if len(args) >= 4:
        return "Либо вы ввели что-то не так, либо вы пытаетесь использовать 2 или более слов(а) в названии реквизита\nЕсли это так – просто назовите_реквизит_таким_образом"
    
    else:
        print(args)
        return "lol"

def register(handlers):
    handlers[".rekv"] = handle
