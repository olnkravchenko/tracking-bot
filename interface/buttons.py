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


def inline_buttons_creation(message: types.Message, page: list, keyboard_interface: types.InlineKeyboardMarkup, page_number: int = 0):
    """
    Create pages in InlineKeyboardButton(s)
    :param message: edited message
    :type message: types.Message
    :param page: array of dictionaries with button's text and callback function
    :type page: list
    :param keyboard_interface: markup of buttons of the edited message
    :type keyboard_interface: types.InlineKeyboardMarkup
    :param page_number: equal to 0 if no arrows required, equal to 1 if it's the first page and 'next' arrow required, equal to 2 if it's the last page and 'previous' arrow required, greater than 1 if both arrows required
    :type page_number: int
    """
    for button in page:
        keyboard_interface.add(
            types.InlineKeyboardButton(text=button['text'], callback_data=button['callback']))

    # create arrow buttons
    if page_number == 0: # first page
        keyboard_interface.add(types.InlineKeyboardButton(text='\U000025B6', callback_data='next_page'))
    elif page_number == 2: # last page
        keyboard_interface.add(types.InlineKeyboardButton(
            text='\U000025C0', callback_data='previous_page'))
    else:
        keyboard_interface.row(types.InlineKeyboardButton(
            text='\U000025C0', callback_data='previous_page'),
            types.InlineKeyboardButton(
            text='\U000025B6', callback_data='next_page'))