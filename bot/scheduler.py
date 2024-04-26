import asyncio
from datetime import datetime

import psutil
from aiogram import Bot
from aiogram.types import Message


async def schedule_message(bot: Bot, chat_id: int):
    message: Message = await bot.send_message(chat_id, "Бот запущен!")
    last_mem_used = 0

    while True:
        start_time = datetime.now()

        current_time = datetime.now().strftime("%H:%M:%S")
        cpu_usage = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        mem_total = mem.total / (1024 ** 3)
        mem_used = mem.used / (1024 ** 3)
        mem_free = mem.free / (1024 ** 3)
        mem_diff = mem_used - last_mem_used
        elapsed_time = (datetime.now() - start_time).total_seconds()

        status_message = (
            f"Последнее обновление: {current_time}\n"
            f"Загрузка CPU: {cpu_usage}%\n"
            f"Общий объем MEM: {mem_total:.2f} GB\n"
            f"Использовано MEM: {mem_used:.2f} GB (Изменение: {mem_diff:.2f} GB)\n"
            f"Свободно MEM: {mem_free:.2f} GB\n"
            f"Цикл обновления занял {elapsed_time:.2f} секунды"
        )
        await message.edit_text(status_message)

        last_mem_used = mem_used

        await asyncio.sleep(5)

