from aiogram import types
from aiogram.types import ContentType

from interface.init_bot import dp, bot
import interface.buttons as buttons


# Create list of start menu buttons with main functionality
start_menu_buttons = [{'text': 'Категории', 'callback': 'categories'},
        {'text': 'Взять технику', 'callback': 'take equipment'},
        {'text': 'Мониторинг', 'callback': 'get history'},]

@dp.message_handler(commands='start')
async def start_menu(message: types.Message):
    """
    Open start menu
    """
    if True: # check user's status, True for member and admin, False for unregistered users
        keyboard_interface = types.InlineKeyboardMarkup(row_width=1).add(*buttons.create_inline_buttons(start_menu_buttons))
        await bot.send_message(chat_id=message.chat.id, text='Привет! Выбери действие ниже', reply_markup=keyboard_interface)
    else:
        # request to admin 
        pass



@dp.callback_query_handler(lambda call: call.data == 'categories')
@buttons.delete_message
async def open_categories(call: types.CallbackQuery):
    """
    Show categories selection
    """
    # Create list of categories
    categories_buttons = [{'text':'\U0001F3A6 Камеры', 'callback':'camera'},
        {'text': '\U0001F4A1 Свет', 'callback':'light'},
        {'text': '\U0001F50A Звук', 'callback':'audio'},
        {'text': '\U0001F3D7 Штативы', 'callback':'tripod'},
        {'text': '\U0001F50B Акумы', 'callback':'battery'},
        {'text': '\U0001F921 Для стримов', 'callback':'broadcast'},]
        # {'text': '\U0000267F Для стримов', 'callback':'broadcast'},]

    await bot.send_message(chat_id=call.message.chat.id, text='Выберите категорию техники', reply_markup=types.InlineKeyboardMarkup().add(*buttons.create_inline_buttons(categories_buttons)))


@dp.callback_query_handler(lambda call: call.data in ['camera','light','audio' ,'tripod','battery','broadcast'])
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
    Show history type selection
    """
