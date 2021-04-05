from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from interface.init_bot import dp, bot
from api import user, equipment, qr_code, transfer, category
import interface.buttons as buttons
from interface.parse_data import parse_qr_code_data


class Add_Equipment(StatesGroup):
    """
    Use states as events for adding equipment
    """
    waiting_for_eq_name_and_owner = State()  # step 1
    waiting_for_category = State()  # step 2
    waiting_for_description = State() # step 3


@dp.callback_query_handler(lambda call: call.data == 'add_eq')
@buttons.delete_message
async def add_equipment_step_1(call: types.CallbackQuery):
    """
    Start adding equipment
    """
    await bot.send_message(chat_id=call.message.chat.id, text='Введите название техники и тэг или id владельца с новой строки.\nПример:\nAvermedia LGP\n@tag_of_owner\n\nЧтобы узнать id пользователя воспользуйтесь @userinfobot')
    await Add_Equipment.waiting_for_eq_name_and_owner.set()


@dp.message_handler(state=Add_Equipment.waiting_for_eq_name_and_owner, content_types=types.ContentTypes.TEXT)
async def add_equipment_step_2(message: types.Message, state: FSMContext):
    """
    Get name and owner of the equipment
    """
    data = message.text.split('\n') # get data in format 'equipment name \n user id or username'
    # get owner data
    owner_data = []
    if data[1].startswith('@'):
        try:
            owner_data = user.get_user_by_username(data[1][1:])
        except Exception as e:
            await bot.send_message(chat_id=message.chat.id, text=f'Пользователь с тэгом {data[1]} не найден. Начните добавление техники заново и попробуйте ввести id пользователя')
    else:
        try:
            owner_data = user.get_user(int(data[1]))
        except Exception as e:
            await bot.send_message(chat_id=message.chat.id, text='Данного пользователя нет в базе данных. Его необходимо зарегистрировать, чтобы добавить технику\nДля возвращения в главное меню напишите /start')
    if owner_data:
        await state.update_data(eq_name=data[0], owner=owner_data['id'])
        await bot.send_message(chat_id=message.chat.id, text='Выберите категорию для техники', reply_markup=buttons.create_categories_buttons())
        await Add_Equipment.next()
    else:
        await state.finish()


@dp.callback_query_handler(lambda call: call.data.startswith('category'), state=Add_Equipment.waiting_for_category)
async def add_equipment_step_3(call: types.CallbackQuery, state: FSMContext):
    """
    Get category of the equipment
    """
    category_id = [cat['name'] for cat in category.get_all_categories()].index(call.data.split()[1]) + 1
    await state.update_data(category=category_id)
    await bot.send_message(chat_id=call.message.chat.id, text='Отправьте описание для техники (до 30 слов)')
    await Add_Equipment.next()


@dp.message_handler(state=Add_Equipment.waiting_for_description, content_types=types.ContentTypes.TEXT)
async def add_equipment_step_4(message: types.Message, state: FSMContext):
    """
    Get description of the equipment and add equipment into DB
    """
    await state.update_data(description=message.text)
    eq_data = await state.get_data()
    await state.finish()
    print(eq_data)
    equipment.add_equipment(eq_data['category'], eq_data['eq_name'], eq_data['owner'], eq_data['description'])
    await bot.send_message(chat_id=message.chat.id, text='Техника была успешно добавлена.\nДля возвращения в главное меню напишите /start')



class Take_Equipment(StatesGroup):
    """
    Use states as events for taking equipment
    """
    scan_qr_code = State()
    waiting_for_confirmation = State()


@dp.callback_query_handler(lambda call: call.data == 'take_equipment')
@buttons.delete_message
async def take_equipment_step_1(call: types.CallbackQuery):
    """
    Request a photo with QR code
    """
    await bot.send_message(chat_id=call.message.chat.id, text='Отправьте фото с QR кодом техники. На одном фото должен быть <b>только один QR код</b>.\nПосле отправки всех QR кодов напишите /ok', parse_mode=types.message.ParseMode.HTML)
    await Take_Equipment.scan_qr_code.set()
    state = dp.current_state()
    await state.update_data(user_items=[], equipment_names=[])


@dp.message_handler(state=Take_Equipment.scan_qr_code, content_types=types.ContentTypes.PHOTO)
async def take_equipment_step_2(message: types.Message, state: FSMContext):
    """
    Get QR code, read data from it and create transfer
    """
    # read data from user's photo with QR code
    eq = await read_qr_code(message)
    eq_buffer = await state.get_data()
    transformed_result = parse_qr_code_data(eq) # get equipment name
    # write data to storage
    await state.update_data(user_items=eq_buffer['user_items']+[eq], equipment_names=eq_buffer['equipment_names']+[transformed_result], user_id=message.chat.id)
    # create transfer
    eq_data = equipment.get_equipment(int(eq.split()[0]))
    transfer.create_transfer(eq_data['id'], eq_data['holder']['id'], message.chat.id)
    await bot.send_message(chat_id=message.chat.id, text=transformed_result)


@dp.message_handler(state=Take_Equipment.scan_qr_code, commands='ok')
async def take_equipment_step_3(message: types.Message, state: FSMContext):
    """
    Ask admins for permission
    """
    eq_buffer = await state.get_data() # list with equipment ids and names
    eq_data = [equipment.get_equipment(int(eq.split()[0])) for eq in eq_buffer['user_items']]
    await bot.send_message(chat_id=message.chat.id, text='Ожидайте подтверждения от администраторов')
    for admin in user.get_admin_list():
         await equipment_confirmation(admin['id'], message.chat.id, eq_buffer)
    await Take_Equipment.next()


@dp.callback_query_handler(lambda call: call.data == 'conf_success', state=Take_Equipment.waiting_for_confirmation)
async def take_equipment_step_4_ok(call: types.CallbackQuery):
    """
    Close transfer and add it to the history
    """
    # get current state
    state = dp.current_state()
    user_id = await state.get_data()
    await state.finish()
    user_id = user_id['user_id'] # get user id
    await bot.send_message(chat_id=user_id, text='Ваша заявка на взятие техники была подтверждена')
    user_transfers = [trans['id'] for trans in transfer.get_active_transfers(user_id)]
    list(map(transfer.verify_transfer, user_transfers))


@dp.callback_query_handler(lambda call: call.data == 'conf_failed', state=Take_Equipment.waiting_for_confirmation)
async def take_equipment_step_4_fail(call: types.CallbackQuery):
    """
    Close transfer and delete it
    """
    # get current state
    state = dp.current_state()
    user_id = await state.get_data()
    await state.finish()
    user_id = user_id['user_id'] # get user id
    await bot.send_message(chat_id=user_id, text='Ваша заявка на взятие техники была отклонена')
    user_transfers = [trans['id'] for trans in transfer.get_active_transfers(user_id)]
    list(map(transfer.delete_transfer, user_transfers))


async def read_qr_code(message: types.Message) -> str:
    """
    Create file from user's photo with QR code and read it
    """
    # create file
    photo = await bot.download_file_by_id(message.photo[0].file_id)
    photo_id = str(message.photo[0].file_id)
    qr_code.save_photo(photo, photo_id)
    # read file
    result = qr_code.get_qr_code_data(qr_code.get_file_path(photo_id))
    # delete file
    qr_code.delete_file(qr_code.get_file_path(photo_id))
    return result


# TODO: delete other messages for other admins
async def equipment_confirmation(admin_id: int, user_id: int, eq_names: list):
    """
    Confirm taking the equipment
    """
    keyboard_interface = buttons.create_inline_markup([{'text': '\U00002705', 'callback': f"conf_success"},{'text': '\U0000274C', 'callback': f"conf_failed"}])

    transformed_eq_names = '\n'.join(eq_names['equipment_names'])
    try:
        username = user.get_user(user_id)['username']
    except:
        username = 'None'
    await bot.send_message(chat_id=admin_id, text=f"Подтвердите передачу техники к {f'@{username}' if username != 'None' else f'[{user_id}](tg://user?id={user_id})'}. Список техники:\n{transformed_eq_names}", reply_markup=keyboard_interface, parse_mode="Markdown")

