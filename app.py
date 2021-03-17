from aiogram import Bot, Dispatcher, executor
from interface.handlers import start_menu
from interface.init_bot import dp

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)