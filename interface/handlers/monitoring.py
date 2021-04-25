from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from datetime import date, timedelta

from interface.init_bot import dp, bot
from api import user, history, equipment
import interface.buttons as buttons
from interface import parse_data as parse
from interface.handlers.equipment import read_qr_code


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
    await bot.send_message(chat_id=call.message.chat.id, text='Отправьте тэг\
 пользователя или его id.\nЧтобы узнать id пользователя воспользуйтесь\
 @userinfobot')
    await Get_User_History.waiting_for_user.set()


@dp.message_handler(state=Get_User_History.waiting_for_user,
                    content_types=types.ContentTypes.TEXT)
async def get_user_history_step_2(message: types.Message, state: FSMContext):
    """
    Get username or user id
    """
    exception_msg = ''

    if message.text.startswith('@'):
        try:
            user_data = user.get_user_by_username(message.text[1:])['id']
        except Exception:
            exception_msg = f'Пользователь с тэгом {message.text} не\
 найден. Начните заново\
 и попробуйте ввести id пользователя'
    else:
        user_data = int(message.text)

    if not exception_msg:
        if user.is_exists(user_data):
            user_history_data = history.get_user_history(user_data)
            if user_history_data:
                transformed_result = parse.parse_history_data(
                    user_history_data)
                await bot.send_message(
                    chat_id=message.chat.id,
                    text=f"История {message.text}:\n{transformed_result}",
                    parse_mode=types.message.ParseMode.HTML)
            else:
                exception_msg = f'История {message.text} пуста'
        else:
            exception_msg = 'Пользователя не существует'

    if exception_msg:
        await bot.send_message(chat_id=message.chat.id,
                               text=exception_msg)
    await state.finish()


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
    yesterday = '.'.join(yesterday)
    today = str(today).split('-')
    today.reverse()
    today = '.'.join(today)
    await bot.send_message(
        chat_id=call.message.chat.id,
        text=f'Отправьте начальную и конечную дату с новой строки.\
 Пример:\n{yesterday}\n{today}')
    await Get_Period_History.waiting_for_period.set()


@dp.message_handler(state=Get_Period_History.waiting_for_period,
                    content_types=types.ContentTypes.TEXT)
async def get_period_history_step_2(message: types.Message, state: FSMContext):
    """
    Get history during specific period
    """
    data = message.text.split('\n')
    period_data = history.get_history_by_period(
        *[int(element)for date in data for element in date.split('.')])
    if period_data:
        transformed_result = parse.parse_history_data(period_data)
        await bot.send_message(
            chat_id=message.chat.id,
            text=f"История с {data[0]} по {data[1]}:\n{transformed_result}",
            parse_mode=types.message.ParseMode.HTML)
    else:
        await bot.send_message(chat_id=message.chat.id,
                               text=f'История с {data[0]} по {data[1]} пуста.')
    await state.finish()


@dp.callback_query_handler(lambda call: call.data == 'my_eq')
@buttons.delete_message
async def my_equipment(call: types.CallbackQuery):
    """
    Get list of user's equipment
    """
    my_eq_data = equipment.get_equipment_by_holder(call.message.chat.id)
    transformed_result = parse.parse_my_equipment_data(my_eq_data)\
        or 'На данный момент у вас нет взятой техники'
    await bot.send_message(chat_id=call.message.chat.id,
                           text=transformed_result)


class Get_Equipment_History(StatesGroup):
    """
    Use states as events for getting history of specific equipment
    """
    scan_qr_code = State()


@dp.callback_query_handler(lambda call: call.data == 'eq_history')
@buttons.delete_message
async def equipment_history_step_1(call: types.CallbackQuery):
    """
    Start getting history of equipment
    """
    await bot.send_message(chat_id=call.message.chat.id, text='Отправьте\
 фото с QR кодом техники. На одном фото должен быть <b>только один QR код</b>',
                           parse_mode=types.message.ParseMode.HTML)
    await Get_Equipment_History.scan_qr_code.set()


@dp.message_handler(state=Get_Equipment_History.scan_qr_code,
                    content_types=types.ContentTypes.PHOTO)
async def equipment_history_step_2(message: types.Message, state: FSMContext):
    """
    Scan QR code
    """
    # read data from QR code
    # TODO: validation control sum
    data = await read_qr_code(message)
    if data:
        try:
            # find equipment history and parse data
            eq_history_data = history.get_equipment_history(
                int(data.split()[0]))
        except Exception:
            transformed_result = 'Техника удалена'
        else:
            if eq_history_data:
                transformed_result = parse.parse_equipment_history_data(
                    eq_history_data)
            else:
                transformed_result = 'История техники пуста'
        await bot.send_message(
            chat_id=message.chat.id,
            text=transformed_result+'\nЧтобы вернуться в главное меню\
 напишите /start',
            parse_mode=types.message.ParseMode.HTML)
        await state.finish()
