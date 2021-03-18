from aiogram import types
from aiogram.types import ContentType

from interface.init_bot import dp, bot
import interface.buttons as buttons
from interface.handlers.user_verification import verification

from api import user

# Create list of start menu buttons with main functionality
start_menu_buttons = [{'text': '\U0001F4CB Категории', 'callback': 'categories'},
        {'text': '\U0001F4F1 Взять технику', 'callback': 'take equipment'},
        {'text': '\U0001F50D Мониторинг', 'callback': 'get history'},]


@dp.message_handler(commands='start')
async def start_menu(message: types.Message):
    """
    Open start menu
    """
    username = message.chat.username or 'None'
    # Register user
    if not user.is_exists(message.chat.id):
        user.create_user(message.chat.id, message.chat.full_name, username)
    # Verify user
    if user.is_verified(message.chat.id):
        keyboard_interface = types.InlineKeyboardMarkup(row_width=1).add(*buttons.create_inline_buttons(start_menu_buttons))
        await bot.send_message(chat_id=message.chat.id, text='Привет! Выбери действие ниже', reply_markup=keyboard_interface)
    else:
        for admin in user.get_admin_list():
            await verification(admin['id'], message.chat.id, f'{username}')


@dp.callback_query_handler(lambda call: call.data == 'categories')
@buttons.delete_message
async def open_categories(call: types.CallbackQuery):
    """
    Show categories selection
    """
    # Create list of categories
    categories_buttons = [{'text':'\U0001F3A6 Камеры', 'callback':'cameras'},
        {'text':'\U0001F52D Объективы', 'callback':'lenses'},
        {'text': '\U0001F4A1 Свет', 'callback':'light'},
        {'text': '\U0001F50A Звук', 'callback':'audio'},
        {'text': '\U0001F3D7 Штативы', 'callback':'tripods'},
        {'text': '\U0001F50B Акумы', 'callback':'battery'},
        {'text': '\U0001F50C Питание', 'callback':'power'},
        {'text': '\U0001F534 Для стримов', 'callback':'broadcast'},]

    await bot.send_message(chat_id=call.message.chat.id, text='Выберите категорию техники', reply_markup=types.InlineKeyboardMarkup().add(*buttons.create_inline_buttons(categories_buttons)))


@dp.callback_query_handler(lambda call: call.data in ['cameras','light','audio','lenses','tripods','battery','power','broadcast',])
async def get_category_list(call: types.CallbackQuery):
    """
    Get list of tech from specific category
    """
   
    await bot.send_message(chat_id=call.message.chat.id,text=call.data)


@dp.callback_query_handler(lambda call: call.data == 'take equipment')
@buttons.delete_message
async def take_equipment(call: types.CallbackQuery):
    """
    Take equipment
    """


@dp.callback_query_handler(lambda call: call.data == 'get history')
@buttons.delete_message
async def get_history(call: types.CallbackQuery):
    """
    Show history
    """
