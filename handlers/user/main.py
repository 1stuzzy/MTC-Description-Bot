from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from loguru import logger

from loader import dp, config, status_names
from data import texts, keyboard
from Package.models import User
from utils import basefunctional
from .menu import show_menu


@dp.message_handler(commands=['start'], state='*')
async def start(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        logger.debug(f"Cancelling state {current_state} in bot start")
        await state.finish()

    chat_id = message.chat.id

    try:
        user = User.get(cid=chat_id)
        await show_menu(chat_id)
        logger.debug(f'[{message.chat.id}]:{user.status}, made /start to bot')
    except User.DoesNotExist:
        logger.debug(f'[{message.chat.id}], first time /start bot')
        await message.answer(text=texts.welcome_text, reply_markup=keyboard.registration_btn())


@dp.callback_query_handler(lambda call: call.data == "return_reg", state='*')
async def continue_reg(call: CallbackQuery, state=FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        logger.debug(f"Cancelling state {current_state} in bot share_phone_info")
        await state.finish()

    await call.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                     text=texts.request_phone_text,
                                     reply_markup=keyboard.phone_info())


@dp.callback_query_handler(lambda call: call.data == "request_phone", state='*')
async def request_phone(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer(texts.phone_text, show_alert=True)
    await call.message.answer_sticker(sticker='CAACAgIAAxkBAAEK1KdlZKq4fDsIWdBcQCx6fvT0YpFeNgAC0xAAAhjuQEtQk1A8OfgXSjME',
                                      reply_markup=await keyboard.share_phone_button())


@dp.message_handler(content_types=['contact'])
async def request_phone(message):
    chat_id = message.chat.id
    name = message.from_user.first_name
    username = message.from_user.username
    phone_number = message.contact.phone_number

    await message.delete()

    user = basefunctional.create_user(chat_id, username, name, phone_number)
    await show_menu(user.cid)

    logger.debug(f'[{chat_id}], Registered!')