from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from interface.init_bot import dp, bot
from api import equipment, qr_code
import interface.buttons as buttons
from interface.parse_data import parse_qr_code_data
from interface.handlers.equipment import read_qr_code

@dp.callback_query_handler(lambda call: call.data == 'delete_user')
@buttons.delete_message
async def delete_user_step_1(call: types.CallbackQuery):
    """
    Start deleting user
    """

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


@dp.message_handler(state=Add_Equipment.waiting_for_eq_name_and_owner,
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
    else:
        try:
            owner_data = user.get_user(int(data[1]))
        except Exception:
            await bot.send_message(chat_id=message.chat.id, text='Данного\
 пользователя нет в базе данных. Его необходимо\
 зарегистрировать, чтобы добавить технику.\nДля возвращения в\
 главное меню напишите /start')
    if owner_data:
        await state.update_data(eq_name=data[0], owner=owner_data['id'])
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


@dp.message_handler(state=Add_Equipment.waiting_for_description,
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
    """
    Use states as events for scanning QR code
    """
    scan_qr_code = State()


@dp.callback_query_handler(lambda call: call.data =='scan_qr_code')
@buttons.delete_message
async def scan_qr_code_step_1(call: types.CallbackQuery):
    """
    Request a photo with QR code
    """ 
    await bot.send_message(chat_id=call.message.chat.id, text='Отправьте фото с QR кодом техники. На одном фото должен быть <b>только один QR код</b>', parse_mode=types.message.ParseMode.HTML)
    await Scan_QR_Code.scan_qr_code.set()


@dp.message_handler(state=Scan_QR_Code.scan_qr_code, content_types=types.ContentTypes.PHOTO)
async def scan_qr_code_step_2(message: types.Message, state:FSMContext):
    """
    Scan QR code
    """
    data = await read_qr_code(message)
    result = parse_qr_code_data(data)
    await bot.send_message(chat_id=message.chat.id, text=result)
    await state.finish()
