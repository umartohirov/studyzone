from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import dp, bot


# Define states
class Registration(StatesGroup):
    name = State()
    phone_number = State()  # State for phone number
    subscription_choice = State()
    payment_proof = State()


@dp.message_handler(text="Subscription")
async def start_registration(message: types.Message):
    await message.reply("Please enter your name:")
    await Registration.name.set()


# Handle name input
@dp.message_handler(state=Registration.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.reply("Please enter your phone number:")
    await Registration.phone_number.set()

# Handle phone number input
@dp.message_handler(state=Registration.phone_number)
async def process_phone_number(message: types.Message, state: FSMContext):
    await state.update_data(phone_number=message.text)


    # Define subscription options
    pricing_options = InlineKeyboardMarkup(row_width=1)
    pricing_options.add(
        InlineKeyboardButton("1 Day - 1.000 sum", callback_data="1_day"),
        InlineKeyboardButton("1 week - 6000 sum", callback_data="1_week"),
        InlineKeyboardButton("1 month - 20 000 sum", callback_data="1_month")
    )
    await message.reply("Please choose a subscription plan:", reply_markup=pricing_options)
    await Registration.subscription_choice.set()

# Handle subscription choice using callback_query
@dp.callback_query_handler(state=Registration.subscription_choice)
async def process_subscription_choice(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(subscription_choice=callback_query.data)

    await bot.send_message(callback_query.from_user.id, "Please upload a screenshot of the payment:",reply_markup=None)
    await Registration.payment_proof.set()

# Handle payment screenshot
@dp.message_handler(content_types=['photo'], state=Registration.payment_proof)
async def process_payment_proof(message: types.Message, state: FSMContext):
    data = await state.get_data()

    # Save payment proof
    payment_proof_file_id = message.photo[-1].file_id
    await state.update_data(payment_proof=payment_proof_file_id)

    # Prepare data for admin review
    name = data['name']
    phone_number = data['phone_number']
    subscription_choice = data['subscription_choice']

    # Create an inline keyboard for admin approval
    admin_keyboard = InlineKeyboardMarkup()
    admin_keyboard.add(InlineKeyboardButton("Approve", callback_data=f"approve:{message.from_user.id}"))
    admin_keyboard.add(InlineKeyboardButton("Reject", callback_data=f"reject:{message.from_user.id}"))

    # Send the information to the admin
    admin_id = '123705109'

    if subscription_choice == '1_day':
        subscription = '1 day'
    elif subscription_choice == '1_week':
        subscription = '1 week'
    elif subscription_choice == '1_month':
        subscription = '1 month'



    await bot.send_photo(admin_id, photo=payment_proof_file_id, reply_markup=admin_keyboard,caption= f"<b>New Registration</b>:\nName: {name}\nPhone Number: {phone_number}\nSubscription: {subscription}",)

    await message.reply("Your registration is under review. You will be notified once it is approved.")
    await state.finish()


from aiogram import types

@dp.callback_query_handler(lambda c: c.data.startswith(('approve', 'reject')))
async def process_admin_action(callback_query: types.CallbackQuery):
    action_data = callback_query.data  # This will be something like 'approve:123456789' or 'reject:123456789'
    action, applicant_id = action_data.split(':')  # Split the action and the applicant's ID

    admin_id = callback_query.from_user.id  # The admin who clicked approve/reject

    # Now you have the applicant_id as a string, so convert it to an integer if necessary
    applicant_id = int(applicant_id)

    if action == 'approve':
        # Remove the inline buttons after the action is taken
        await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                            message_id=callback_query.message.message_id,
                                            reply_markup=None)
        await bot.send_message(admin_id, "You have successfully approved the registration.")
        await bot.send_message(applicant_id, "Your registration has been approved!")

    elif action == 'reject':
        # Remove the inline buttons after the action is taken
        await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                            message_id=callback_query.message.message_id,
                                            reply_markup=None)
        await bot.send_message(admin_id, "You have successfully rejected the registration.")
        await bot.send_message(applicant_id, "Your registration has been rejected.")

