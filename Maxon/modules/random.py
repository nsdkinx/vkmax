from Maxon.init import VERSION, START_TIME
import random

__name__ = "Random"
__description__ = "Возвращает случайное число из заданного диапазона"
__version__ = "1.0.0"
__author__ = "@RATcraftGames"

async def handle(packet, args):
    if len(args) != 2:
        return "Использование: .random [начальное число] [конечное число]"
    try:
        start = int(args[0])
        end = int(args[1])
    except ValueError:
        return "Ошибка: оба аргумента должны быть целыми числами."
    if start > end:
        return "Ошибка: начальное число должно быть меньше или равно конечному."
    result = random.randint(start, end)
    return f"🎲 {result}"

def register(handlers):
    handlers[".random"] = handle 
