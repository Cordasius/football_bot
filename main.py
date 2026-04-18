# main.py
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers.common import router as common_router
from handlers.match_create import router as match_create_router
from handlers.match_status import router as match_status_router
from handlers.match_rsvp import router as match_rsvp_router


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(common_router)
    dp.include_router(match_create_router)
    dp.include_router(match_status_router)
    dp.include_router(match_rsvp_router)

    logger.info("🤖 Bot starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())