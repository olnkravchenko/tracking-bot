from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from datetime import date, timedelta

from interface.init_bot import dp, bot
from api import user, history
import interface.buttons as buttons
from interface import parse_data as parse


class Get_User_History(StatesGroup):
    """
    Use states as events for getting user history
    """
    waiting_for_user = State()  # step 1


@dp.callback_query_handler(lambda call: call.data == 'user_history')
async def get_user_history_step_1(call: types.CallbackQuery):
    """
    Start of getting user history
    """
    await bot.send_message(chat_id=call.message.chat.id, text='Введите тэг пользователя или его id.\nЧтобы узнать id пользователя воспользуйтесь @userinfobot')
    await Get_User_History.waiting_for_user.set()


@dp.message_handler(state=Get_User_History.waiting_for_user, content_types=types.ContentTypes.TEXT)
async def get_user_history_step_2(message: types.Message):
    """
    Get username or user id
    """
    if message.text.startswith('@'):
        user_data = history.get_user_history(user.get_user_by_username(message.text[1:])['id'])
    else:
        user_data = history.get_user_history(int(message.text))

    if user_data:
        transformed_result = parse.parse_history_data(user_data)
        await bot.send_message(chat_id=message.chat.id, text=f"История {message.text}:\n{transformed_result}", parse_mode=types.message.ParseMode.HTML)
    else:
        await bot.send_message(chat_id=message.chat.id, text=f'История {message.text} пуста.')



class Get_Period_History(StatesGroup):
    """
    Use states as events for getting history during specific period
    """
    waiting_for_period = State()  # step 1


@dp.callback_query_handler(lambda call: call.data == 'during_time')
async def get_period_history_step_1(call: types.CallbackQuery):
    """
    Start of getting history during specific period
    """
    today = date.today()
    yesterday = str(today - timedelta(days=1)).split('-')
    yesterday.reverse()
    yesterday =  '.'.join(yesterday)
    today = str(today).split('-')
    today.reverse()
    today = '.'.join(today)
    await bot.send_message(chat_id=call.message.chat.id, text=f'Введите начальную и конечную дату с новой строки. Пример:\n{yesterday}\n{today}')
    await Get_Period_History.waiting_for_period.set()


@dp.message_handler(state=Get_Period_History.waiting_for_period, content_types=types.ContentTypes.TEXT)
async def get_period_history_step_2(message: types.Message):
    """
    Get history during specific period
    """
    data = message.text.split('\n')
    period_data = history.get_history_by_period(*[int(element) for date in data for element in date.split('.')])
    if period_data:
        transformed_result = parse.parse_history_data(period_data)
        await bot.send_message(chat_id=message.chat.id, text=f"История с {data[0]} по {data[1]}:\n{transformed_result}", parse_mode=types.message.ParseMode.HTML)
    else:
        await bot.send_message(chat_id=message.chat.id, text=f'История с {data[0]} по {data[1]} пуста.')
