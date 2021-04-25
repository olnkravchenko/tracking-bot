from aiogram import types

from interface.init_bot import bot
from api.category import get_all_categories
from api.equipment import get_equipment_by_holder
from api.user import is_admin


def create_inline_buttons(buttons_list: list) -> list:
    """
    Create generator of InlineKeyboardButtons
    """
    return (types.InlineKeyboardButton(text=button_info['text'],
            callback_data=button_info['callback'])
            for button_info in buttons_list)


def create_inline_markup(buttons_list: list, row_width: int = 3)\
                         -> types.InlineKeyboardMarkup:
    """
    Create inline keyboard markup using function add() by default
    """
    return types.InlineKeyboardMarkup(row_width=row_width).add(
        *create_inline_buttons(buttons_list))


def create_start_menu_buttons(user_id: int):
    """
    Create list of start menu buttons with main functionality
    """
    start_menu_buttons = [
        {'text': '\U0001F4CB Категории', 'callback': 'categories'},
        {'text': '\U0001F4F1 Взять технику', 'callback': 'take_equipment'},
        {'text': '\U0001F50D Мониторинг', 'callback': 'get_history'},
        {'text': '\U0001F9D0 Отсканировать QR код', 'callback': 'scan_qr_code'}
        ]
            {'text':'\U0001F9D0	Отсканировать QR код','callback':'scan_qr_code'}]
    if is_admin:
        start_menu_buttons.append({'text': '\U0001F9D1 Админская панель', 'callback': 'admin_panel'})
    
    if is_admin(user_id):
        start_menu_buttons.append(
            {'text': '\U0001F9D1 Админская панель', 'callback': 'admin_panel'})

    return create_inline_buttons(start_menu_buttons)


def create_categories_buttons():
    """
    Create list of categories
    """
    categories = [cat['name'] for cat in get_all_categories()]
    # create buttons text
    categories_buttons = [{'text': '\U0001F3A6 Камеры'},
                          {'text': '\U0001F4A1 Свет'},
                          {'text': '\U0001F50A Звук'},
                          {'text': '\U0001F52D Объективы'},
                          {'text': '\U0001F3D7 Штативы'},
                          {'text': '\U0001F50B Акумы'},
                          {'text': '\U0001F50C Питание'},
                          {'text': '\U0001F534 Для стримов'}]
    # create buttons callback
    for index, cat in enumerate(categories):
        categories_buttons[index]['callback'] = f"category {cat}"

    return create_inline_markup(categories_buttons)


def delete_message(func):
    """
    Delete message that triggered the callback
    """
    async def wrapper(*args):
        if isinstance(args[0], types.CallbackQuery):
            call = args[0]
            await bot.delete_message(call.message.chat.id,
                                     call.message.message_id)
        elif isinstance(args[0], types.Message):
            message = args[0]
            await bot.delete_message(message.chat.id, message.message_id)
        await func(*args)

    return wrapper


# def delete_after_event(func, messages):
#     """
#     Delete all messages after event
#     """
#     async def wrapper(*args):
#         for message in messages:
            

#     return wrapper
