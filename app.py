from aiogram import executor
from interface.init_bot import dp
from interface.handlers import start_menu

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
