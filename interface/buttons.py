from aiogram import types

from interface.init_bot import dp, bot

def create_inline_buttons(buttons_list: list) -> list:
    """
    Create generator of InlineKeyboardButtons
    """
    return (types.InlineKeyboardButton(text=button_info['text'],
     callback_data=button_info['callback']) for button_info in buttons_list)


def delete_message(func):
    """
    Delete message that triggered the callback
    """
    async def wrapper(call: types.CallbackQuery):
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await func(call)

    return wrapper