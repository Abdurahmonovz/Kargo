import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import load_config
from db import DB
from handlers import start_router, order_router, payment_router, admin_router

async def main():
    config = load_config()

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher()

    db = DB(config.db_path)
    await db.init()

    dp.include_router(start_router)
    dp.include_router(order_router)
    dp.include_router(payment_router)
    dp.include_router(admin_router)

    await dp.start_polling(bot, db=db, config=config)

if __name__ == "__main__":
    asyncio.run(main())