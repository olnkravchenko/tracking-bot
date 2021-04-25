from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import logging

from config import TOKEN

# configure logging
logging.basicConfig(level=logging.INFO)

# initialize bot and dispatcher
bot = Bot(token=TOKEN)
memory_storage = MemoryStorage()
dp = Dispatcher(bot, storage=memory_storage)
