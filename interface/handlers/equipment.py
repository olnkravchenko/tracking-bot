from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from interface.init_bot import dp, bot
from api import user, equipment
import interface.buttons as buttons


class Add_Equipment(StatesGroup):
    """
    Use states as events for adding equipment
    """
    waiting_for_eq_name_and_owner = State()  # step 1
    waiting_for_description = State()  # step 2


@dp.callback_query_handler(lambda call: call.data.startswith('add equipment'))
@buttons.delete_message
async def add_equipment_step_1(call: types.CallbackQuery, state: FSMContext):
    """
    Start adding equipment
    """
    await bot.send_message(chat_id=call.message.chat.id, text='Введите название техники и тэг или id владельца с новой строки.\nПример:\nAvermedia LGP\n@tag_of_owner\n\nЧтобы узнать id пользователя воспользуйтесь @userinfobot')
    await Add_Equipment.waiting_for_eq_name_and_owner.set()
    await state.update_data(category_id=int(call.data.split()[2]))


@dp.message_handler(state=Add_Equipment.waiting_for_eq_name_and_owner, content_types=types.ContentTypes.TEXT)
async def add_equipment_step_2(message: types.Message, state: FSMContext):
    """
    Get name and owner of the equipment
    """
    data = message.text.split('\n')
    # TODO: handle exceptions
    if data[1].startswith('@'):
        owner_data = user.get_user_by_username(data[1][1:])
    else:
        owner_data = user.get_user(int(data[1]))
    if owner_data and (user.is_admin(owner_data['id']) or owner_data['id'] == 1):
        await state.update_data(name=data[0], owner=data[1][1:])
        await bot.send_message(chat_id=message.chat.id, text='Введите описание техники.')
        await Add_Equipment.next()
    else:
        await bot.send_message(chat_id=message.chat.id, text='Можно добавлять только технику админов. Добавление техники остановлено.')
        await state.finish()


@dp.message_handler(state=Add_Equipment.waiting_for_eq_name_and_owner, content_types=types.ContentTypes.TEXT)
async def add_equipment_step_3(message: types.Message, state: FSMContext):
    """
    Get description of the equipment
    """
    await state.update_data(description=message.text)
    user_data = await state.get_data()
    await state.finish()
    print(user_data)

    equipment.add_equipment(user_data['category_id'], user_data['name'], user_data['owner'], user_data['description'])
    await bot.send_message(chat_id=message.chat.id, text='Техника была успешно добавлена.\nДля возвращения в главное меню напишите /start')



class Take_Equipment(StatesGroup):
    """
    Use states as events for taking equipment
    """
    waiting_for_qr_code = State()  # step 1
    waiting_for_confirmation = State()  # step 2


@dp.callback_query_handler(lambda call: call.data.startswith('add equipment'))
@buttons.delete_message
async def add_equipment_step_1(call: types.CallbackQuery, state: FSMContext):
    """
    Start taking the equipment
    """

