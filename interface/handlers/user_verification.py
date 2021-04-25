from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from interface.init_bot import dp, bot
import interface.buttons as buttons
from api import user


class Verification(StatesGroup):
    """
    Use states as events for deleting messages after verification
    """
    waiting_for_action = State()  # step 1


# TODO: delete other messages for other admins
async def verification(admin_id: int, user_id: int,
                       username: str = None):
    keyboard_interface = buttons.create_inline_markup(
        [{'text': '\U00002705', 'callback': f'verification success {user_id}'},
         {'text': '\U0000274C', 'callback': f'verification failed {user_id}'}])
    user_name = f'@{username}' if username is not None else \
        f'[{user_id}](tg://user?id={user_id})'
    message = await bot.send_message(
        chat_id=admin_id,
        text=f"Подтвердите пользователя {user_name}",
        reply_markup=keyboard_interface,
        parse_mode="Markdown")
    # TODO: check states
    await Verification.waiting_for_action.set()
    state = dp.current_state()
    messages_list = await state.get_data()
    print(messages_list)
    messages_list = messages_list['admin_messages'] if messages_list else []
    await state.update_data(
        admin_messages=messages_list + [message])


@dp.callback_query_handler(lambda call:
                           call.data.startswith('verification success'))
# @buttons.delete_message
async def verification_success(call: types.CallbackQuery, state: FSMContext):
    state = dp.current_state()
    messages_data = await state.get_data()
    for message in messages_data['admin_messages']:
        await bot.delete_message(message.chat.id, message.message_id)
    user_id = int(call.data.split()[2])
    user.verify_user(user_id)
    await bot.send_message(chat_id=user_id, text='Вы получили доступ к боту.\
 Пропишите /start для использования')
    await state.finish()


@dp.callback_query_handler(lambda call:
                           call.data.startswith('verification failed'),
                           state=Verification.waiting_for_action)
# @buttons.delete_message
async def verification_failed(call: types.CallbackQuery, state: FSMContext):
    messages_data = await state.get_data()
    for message in messages_data['admin_messages']:
        await bot.delete_message(message.chat.id, message.message_id)
    user_id = int(call.data.split()[2])
    await bot.send_message(chat_id=user_id,
                           text='Администраторы отклонили вашу заявку')
    await state.finish()
