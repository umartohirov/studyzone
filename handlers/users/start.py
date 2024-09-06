from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import dp, bot



# Start the registration process
@dp.message_handler(CommandStart)
async def start(message: types.Message):
    main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    main_menu.add(types.KeyboardButton("Subscription"))

    await message.answer("Welcome to Study Zone, here you can purchase our services", reply_markup=main_menu)

