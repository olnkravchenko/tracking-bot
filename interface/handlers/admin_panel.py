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



class Scan_QR_Code(StatesGroup):
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
