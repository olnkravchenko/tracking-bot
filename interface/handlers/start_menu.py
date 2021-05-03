from aiogram import types
from logging import info, warning

from interface.init_bot import dp, bot
import interface.buttons as buttons
from interface.handlers import user_verification, equipment, monitoring, admin_panel
from interface import parse_data as parse

from api import user, category, history


@dp.callback_query_handler(lambda call: call.data == 'start_menu')
@dp.message_handler(commands='start')
@buttons.delete_message
async def start_menu(call):
    """
    Open start menu
    """
    message = call.message if isinstance(call, types.CallbackQuery) else call
    username = message.chat.username or None
    # add user to the db
    registration_flag = False
    if not user.is_exists(message.chat.id):
        registration_flag = True
        user.create_user(message.chat.id, message.chat.full_name, username)
        await bot.send_message(
            chat_id=message.chat.id,
            text='Ожидайте подтверждения от администраторов')
        # verify user
        await user_verification.notify_admins(message, username)
    if user.is_verified(message.chat.id):
        # check if username in the DB is up to date
        check_username(message)
        keyboard_interface = types.InlineKeyboardMarkup(row_width=1).add(
            *buttons.create_start_menu_buttons(message.chat.id))
        await bot.send_message(chat_id=message.chat.id,
                               text='Привет! Выберите действие ниже',
                               reply_markup=keyboard_interface)
    elif not registration_flag:
        await bot.send_message(chat_id=message.chat.id, text='Извините, вы не\
 верифицированы. В случае, если это ошибка, обратитесь к администраторам')


@dp.callback_query_handler(lambda call: call.data == 'categories')
@buttons.delete_message
async def open_categories(call: types.CallbackQuery):
    """
    Show categories selection
    """
    await bot.send_message(chat_id=call.message.chat.id,
                           text='Выберите категорию техники',
                           reply_markup=buttons.create_categories_buttons())


@dp.callback_query_handler(lambda call: call.data.startswith('category'))
async def get_category_equipment_list(call: types.CallbackQuery):
    """
    Get list of tech from specific category
    """
    # create list of categories from DB
    categories = [cat['name'] for cat in category.get_all_categories()]
    try:
        data = category.get_category_equipment(categories.index(
            call.data.split()[1]) + 1)
    except Exception:
        data = []
        await bot.send_message(chat_id=call.message.chat_id,
                               text='Данной категории не существует')
    # TODO: write pages for equipment list of the category
    if data:
        transformed_data = parse.parse_category_equipment_data(data)[0]
        await bot.send_message(
            chat_id=call.message.chat.id,
            text=transformed_data, parse_mode=types.message.ParseMode.HTML)
    else:
        await bot.send_message(chat_id=call.message.chat.id,
                               text='В данной категории нет техники')


@dp.callback_query_handler(lambda call: call.data == 'get_history')
@buttons.delete_message
async def get_history(call: types.CallbackQuery):
    """
    Show history
    """
    data = history.get_last_actions(count=20)
    history_buttons = [
        {'text': 'За период времени', 'callback': 'during_time'},
        {'text': 'Моя техника', 'callback': 'my_eq'},
        {'text': 'История техники', 'callback': 'eq_history'}]
    if user.is_admin(call.message.chat.id):
        history_buttons += [
            {'text': 'История пользователя', 'callback': 'user_history'}]
    if data:
        transformed_data = parse.parse_history_data(data)
        await bot.send_message(
            chat_id=call.message.chat.id,
            text=transformed_data,
            reply_markup=buttons.create_inline_markup(history_buttons),
            parse_mode=types.message.ParseMode.HTML)
    else:
        await bot.send_message(chat_id=call.message.chat.id,
                               text='История пуста',
                               reply_markup=buttons.create_inline_markup(
                                    history_buttons, row_width=2))


@dp.callback_query_handler(lambda call: call.data == 'admin_panel')
@buttons.delete_message
async def admin_menu(call: types.CallbackQuery):
    """
    Admin panel
    """
    admin_markup = buttons.create_inline_markup(
        [{'text': 'Добавить технику', 'callback': 'add_eq'},
         {'text': 'Удалить технику', 'callback': 'delete_eq'},
         {'text': 'Удалить пользователя', 'callback': 'delete_user'},
         {'text': 'Изменить описание техники', 'callback': 'change_desc'},
         {'text': 'Вернуться назад', 'callback': 'start_menu'}], row_width=2)

    await bot.send_message(chat_id=call.message.chat.id,
                           text='Привет! Выберите действие ниже',
                           reply_markup=admin_markup)


def check_username(message: types.Message):
    """
    Check if username in the DB is up to date and change it if it is not
    """
    try:
        user.get_user_by_username(message.chat.username)
    except Exception:
        user.change_username(message.chat.id, message.chat.username)


@dp.message_handler(commands='cancel', state="*")
async def cancel_current_state(message: types.Message):
    """
    Allow user to cancel any action
    """
    state = dp.current_state()
    info(f'Cancelling state ({state}) by {message.chat.id}...')
    await state.finish()
    await bot.send_message(chat_id=message.chat.id, text='\U0001F44C')
