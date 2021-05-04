from aiogram import executor
import timer
from interface.init_bot import dp
from interface.handlers import start_menu
from daemon import main as daemon

if __name__ == '__main__':
    timer_instance = timer.Timer(2*24*60*60, daemon, True, False)
    executor.start_polling(dp, skip_updates=True)
