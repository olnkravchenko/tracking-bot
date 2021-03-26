from aiogram import types
from aiogram.types import ContentType

from interface.init_bot import dp, bot
import interface.buttons as buttons
from interface.handlers.user_verification import verification
from interface import parse_data as parse

from api import user, category, history


@dp.message_handler(commands='start')
async def start_menu(message: types.Message):
    """
    Open start menu
    """
    username = message.chat.username or 'None'
    # Register user
    if not user.is_exists(message.chat.id):
        user.create_user(message.chat.id, message.chat.full_name, username)
        for admin in user.get_admin_list():
            await user_verification.verification(admin['id'], message.chat.id, f'{username}') # Verify user
    if user.is_verified(message.chat.id):
        keyboard_interface = types.InlineKeyboardMarkup(row_width=1).add(*buttons.create_start_menu_buttons(user.is_admin(message.chat.id)))
        await bot.send_message(chat_id=message.chat.id, text='Привет! Выбери действие ниже', reply_markup=keyboard_interface)
    else:
        await bot.send_message(chat_id=message.chat.id, text='Извините, вы не верифицированы. В случае, если это ошибка, обратитесь к администраторам.')



@dp.callback_query_handler(lambda call: call.data == 'categories')
@buttons.delete_message
async def open_categories(call: types.CallbackQuery):
    """
    Show categories selection
    """
    # Create list of categories from DB
    categories = [cat['name'] for cat in category.get_all_categories()]
    categories_buttons = [{'text': '\U0001F3A6 Камеры'},
                        {'text': '\U0001F52D Объективы'}, 
                        {'text': '\U0001F4A1 Свет'}, 
                        {'text': '\U0001F50A Звук'}, 
                        {'text': '\U0001F3D7 Штативы'}, 
                        {'text': '\U0001F50B Акумы'}, 
                        {'text': '\U0001F50C Питание'}, 
                        {'text': '\U0001F534 Для стримов'}]
    for index, cat in enumerate(categories):
        categories_buttons[index]['callback'] = f"category {cat}"

    await bot.send_message(chat_id=call.message.chat.id, text='Выберите категорию техники', reply_markup=buttons.create_inline_markup(categories_buttons))


@dp.callback_query_handler(lambda call: call.data.startswith('category'))
async def get_category_equipment_list(call: types.CallbackQuery):
    """
    Get list of tech from specific category
    """
    # Create list of categories from DB
    categories = [cat['name'] for cat in category.get_all_categories()]
    data = category.get_category_equipment(categories.index(call.data.split()[1]) + 1)

    if data:
        transformed_data = parse.parse_category_equipment_data(data)
        bot_message = await bot.send_message(chat_id=call.message.chat.id, text=transformed_data, parse_mode=types.message.ParseMode.HTML)
    else:
        bot_message = await bot.send_message(chat_id=call.message.chat.id, text='В данной категории нет техники')


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
