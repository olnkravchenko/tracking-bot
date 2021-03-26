from aiogram import types

from interface.init_bot import dp, bot


def create_inline_buttons(buttons_list: list) -> list:
    """
    Create generator of InlineKeyboardButtons
    """
    return (types.InlineKeyboardButton(text=button_info['text'],
     callback_data=button_info['callback']) for button_info in buttons_list)


def create_inline_markup(buttons_list: list, row_mode: bool = False) -> types.InlineKeyboardMarkup:
    """
    Create inline keyboard markup using function add() by default
    """
    if not row_mode:
        return types.InlineKeyboardMarkup().add(*create_inline_buttons(buttons_list))
    else:
        return types.InlineKeyboardMarkup().row(*create_inline_buttons(buttons_list))


def create_start_menu_buttons(is_admin: bool):
    """
    Create list of start menu buttons with main functionality
    """
    start_menu_buttons = [{'text': '\U0001F4CB Категории', 'callback': 'categories'},
            {'text': '\U0001F4F1 Взять технику', 'callback': 'take equipment'},
            {'text': '\U0001F50D Мониторинг', 'callback': 'get history'}]
    if is_admin:
        start_menu_buttons.append({'text': '\U0001F9D1 Админская панель', 'callback': 'admin_panel'})
    
    return create_inline_buttons(start_menu_buttons)


def delete_message(func):
    """
    Delete message that triggered the callback
    """
    async def wrapper(*args):
        if type(args[0]) == types.CallbackQuery:
            call = args[0]
            await bot.delete_message(call.message.chat.id, call.message.message_id)
        elif type(args[0]) == types.Message:
            message = args[0]
            await bot.delete_message(message.chat.id, message.message_id)
        await func(*args)

    return wrapper