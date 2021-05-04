from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from interface.init_bot import dp, bot
from api import equipment, category, user
import interface.buttons as buttons
from interface.handlers.equipment import read_qr_code
from interface.parse_data import validate_qr_code


class Delete_User(StatesGroup):
    """
    Use states as events for deleting user
    """
    waiting_for_user_id = State()  # step 1


@dp.callback_query_handler(lambda call: call.data == 'delete_user')
@buttons.delete_message
async def delete_user_step_1(call: types.CallbackQuery):
    """
    Start deleting user
    """
    await bot.send_message(chat_id=call.message.chat.id,
                           text='Отправьте тэг пользователя или его id.\nЧтобы\
 узнать id пользователя воспользуйтесь\
 @userinfobot')
    await Delete_User.waiting_for_user_id.set()


@dp.message_handler(lambda message: not message.text.startswith('/'),
                    state=Delete_User.waiting_for_user_id,
                    content_types=types.ContentTypes.TEXT)
async def delete_user_step_2(message: types.Message, state: FSMContext):
    """
    Get user name or id
    """
    exception_msg = ''
    if message.text.startswith('@'):
        try:
            user_data = user.get_user_by_username(message.text[1:])['id']
        except Exception:
            exception_msg = f'Пользователь с тэгом {message.text} не\
 найден. Начните заново\
 и попробуйте ввести id пользователя'
    else:
        user_data = int(message.text)

    if not exception_msg:
        if user.is_exists(user_data):
            user.delete_user(user_data)
            await bot.send_message(chat_id=message.chat.id,
                                   text='Пользователь был успешно удалён')
        else:
            exception_msg = 'Пользователя не существует'

    if exception_msg:
        await bot.send_message(chat_id=message.chat.id,
                               text=exception_msg)
    await state.finish()


class Add_Equipment(StatesGroup):
    """
    Use states as events for adding equipment
    """
    waiting_for_eq_name_and_owner = State()  # step 1
    waiting_for_category = State()  # step 2
    waiting_for_description = State()  # step 3


@dp.callback_query_handler(lambda call: call.data == 'add_eq')
@buttons.delete_message
async def add_equipment_step_1(call: types.CallbackQuery):
    """
    Start adding equipment
    """
    await bot.send_message(chat_id=call.message.chat.id, text='Отправьте\
 название техники и тэг или id владельца с новой строки.\
 \nПример:\nAvermedia LGP\n@tag_of_owner\n\nЧтобы узнать id пользователя\
  воспользуйтесь @userinfobot')
    await Add_Equipment.waiting_for_eq_name_and_owner.set()


@dp.message_handler(lambda message: not message.text.startswith('/'),
                    state=Add_Equipment.waiting_for_eq_name_and_owner,
                    content_types=types.ContentTypes.TEXT)
async def add_equipment_step_2(message: types.Message, state: FSMContext):
    """
    Get name and owner of the equipment
    """
    # get data in format 'equipment name \n user id or username'
    data = message.text.split('\n')
    # get owner data
    owner_data = []
    if data[1].startswith('@'):
        try:
            owner_data = user.get_user_by_username(data[1][1:])
        except Exception:
            await bot.send_message(chat_id=message.chat.id,
                                   text=f'Пользователь с тэгом {data[1]} не\
 найден. Начните добавление техники заново\
 и попробуйте ввести id пользователя')
    elif data[1] == 'Штаб':
        try:
            owner_data = user.get_user_by_username(data[1])
        except Exception:
            await bot.send_message(chat_id=message.chat.id,
                                   text=f'Пользователь с тэгом {data[1]} не\
 найден. Начните добавление техники заново\
 и попробуйте ввести id пользователя')
    else:
        try:
            owner_data = user.get_user(int(data[1]))
        except Exception:
            await bot.send_message(chat_id=message.chat.id, text='Данного\
 пользователя нет в базе данных. Его необходимо\
 зарегистрировать, чтобы добавить технику.\nДля возвращения в\
 главное меню напишите /start')
    if owner_data:
        await state.update_data(eq_name=data[0].strip(), owner=owner_data['id'])
        await bot.send_message(chat_id=message.chat.id,
                               text='Выберите категорию для техники',
                               reply_markup=buttons.create_categories_buttons()
                               )
        await Add_Equipment.next()
    else:
        await state.finish()


@dp.callback_query_handler(lambda call: call.data.startswith('category'),
                           state=Add_Equipment.waiting_for_category)
async def add_equipment_step_3(call: types.CallbackQuery, state: FSMContext):
    """
    Get category of the equipment
    """
    category_id = [cat['name'] for cat in category.get_all_categories()].index(
        call.data.split()[1]) + 1
    await state.update_data(category=category_id)
    await bot.send_message(chat_id=call.message.chat.id,
                           text='Отправьте описание для техники (до 30 слов)')
    await Add_Equipment.next()


@dp.message_handler(lambda message: not message.text.startswith('/'),
                    state=Add_Equipment.waiting_for_description,
                    content_types=types.ContentTypes.TEXT)
async def add_equipment_step_4(message: types.Message, state: FSMContext):
    """
    Get description of the equipment and add equipment into DB
    """
    await state.update_data(description=message.text)
    eq_data = await state.get_data()
    await state.finish()
    try:
        equipment.add_equipment(eq_data['category'], eq_data['eq_name'],
                                eq_data['owner'], eq_data['description'])
        await bot.send_message(chat_id=message.chat.id,
                            text='Техника была успешно добавлена.\nДля\
 возвращения в главное меню напишите /start')
    except Exception:
        await bot.send_message(chat_id=message.chat.id,
                               text='Произошла ошибка. Попробуйте ещё раз')


class Delete_Equipment(StatesGroup):
    """
    Use states as events for deleting the equipment
    """
    waiting_for_equipment_info = State()  # step 1


@dp.callback_query_handler(lambda call: call.data == 'delete_eq')
@buttons.delete_message
async def delete_equipment_step_1(call: types.CallbackQuery):
    """
    Start deleting the equipment
    """
    await bot.send_message(chat_id=call.message.chat.id,
                           text='Отправьте полное название техники или QR код')
    await Delete_Equipment.waiting_for_equipment_info.set()


@dp.message_handler(lambda message: not message.text.startswith('/'),
                    state=Delete_Equipment.waiting_for_equipment_info,
                    content_types=types.ContentTypes.TEXT)
async def delete_eq_by_name(message: types.Message, state: FSMContext):
    """
    Get equipment name
    """
    try:
        equipment_id = equipment.get_equipment_by_name(message.text)['id']
    except Exception:
        await bot.send_message(chat_id=message.chat.id,
                               text=f'Техники с названием "{message.text}"\
 не существует')
    else:
        equipment.delete_equipment(equipment_id)
        await bot.send_message(chat_id=message.chat.id,
                               text='Техника была успешно удалена')
    await state.finish()


@dp.message_handler(state=Delete_Equipment.waiting_for_equipment_info,
                    content_types=types.ContentTypes.PHOTO)
async def delete_eq_by_qrcode(message: types.Message, state: FSMContext):
    """
    Get equipment name from QR code
    """
    qr_code_data = await read_qr_code(message)
    if qr_code_data:
        if not validate_qr_code(qr_code_data):
            await bot.send_message(chat_id=message.chat.id,
                             text='Произошла ошибка в считывании QR кода.\
 Попробуйте ещё раз' )
        else:
            equipment_id = int(qr_code_data.split()[0])
            equipment.delete_equipment(equipment_id)
            await bot.send_message(chat_id=message.chat.id,
                                   text='Техника была успешно удалена')
    await state.finish()


class Change_Description(StatesGroup):
    """
    Use states as events for changing description of equipment
    """
    waiting_for_equipment_info = State()  # step 1
    waiting_for_description = State()  # step 2


@dp.callback_query_handler(lambda call: call.data == 'change_desc')
@buttons.delete_message
async def change_desc_step_1(call: types.CallbackQuery):
    """
    Start changing description of the equipment
    """
    await bot.send_message(chat_id=call.message.chat.id,
                           text='Отправьте полное название техники или QR код')
    await Change_Description.waiting_for_equipment_info.set()


@dp.message_handler(lambda message: not message.text.startswith('/'),
                    state=Change_Description.waiting_for_equipment_info,
                    content_types=types.ContentTypes.TEXT)
async def change_desc_by_name(message: types.Message, state: FSMContext):
    """
    Get equipment name
    """
    try:
        equipment_id = equipment.get_equipment_by_name(message.text)['id']
    except Exception:
        await bot.send_message(chat_id=message.chat.id,
                               text=f'Техники с названием "{message.text}"\
 не существует')
        await state.finish()
    else:
        await state.update_data(eq_id=equipment_id)
        await bot.send_message(chat_id=message.chat.id,
                               text='Отправьте описание техники (до 30 слов)')
        await Change_Description.next()


@dp.message_handler(state=Change_Description.waiting_for_equipment_info,
                    content_types=types.ContentTypes.PHOTO)
async def change_desc_by_qrcode(message: types.Message, state: FSMContext):
    """
    Get equipment name from QR code
    """
    qr_code_data = await read_qr_code(message)
    if qr_code_data:
        if not validate_qr_code(qr_code_data):
            await bot.send_message(chat_id=message.chat.id,
                             text='Произошла ошибка в считывании QR кода.\
 Попробуйте ещё раз' )
            await state.finish()
        else:
            equipment_id = int(qr_code_data.split()[0])
            equipment.get_equipment(equipment_id)
            await state.update_data(eq_id=equipment_id)
            await bot.send_message(
                chat_id=message.chat.id,
                text='Отправьте описание техники (до 30 слов)')
            await Change_Description.next()


@dp.message_handler(lambda message: not message.text.startswith('/'),
                    state=Change_Description.waiting_for_description,
                    content_types=types.ContentTypes.TEXT)
async def change_desc_step_3(message: types.Message, state: FSMContext):
    """
    Get new description of the equipment and change it
    """
    eq_id = await state.get_data()
    eq_id = eq_id['eq_id']
    equipment.change_equipment_description(eq_id, message.text)
    await bot.send_message(chat_id=message.chat.id,
                           text='Описание техники было успешно изменено')
    await state.finish()
