import asyncio
import logging
from sched import scheduler

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from api.coinmarketcap import monitor
from bot.scheduler import schedule_message
from config import cfg
from bot.handler.handlers import router
from database.queries.core import AsyncORM


async def on_startup(dp: Dispatcher):
    dp.include_router(router)


async def main() -> None:
    bot = Bot(token=cfg.TELEGRAM_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    await on_startup(dp)
    await bot.delete_webhook(drop_pending_updates=True)
    await AsyncORM.create_table()

    asyncio.create_task(schedule_message(bot, cfg.CHANNEL_ID)),
    asyncio.create_task(monitor(cfg.COINMARKET_API_KEY, bot, cfg.MAX_WORKERS))

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())