import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import ParseMode
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from Package.customutils.config import load_config
from utils.status import StatusNames

config = load_config()

status_names = StatusNames()

loop = asyncio.get_event_loop()

bot = Bot(config.api_token, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot, loop=loop, storage=MemoryStorage())