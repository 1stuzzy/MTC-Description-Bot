from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.dispatcher import FSMContext
from loguru import logger

from loader import dp, config, status_names
from data import texts, keyboard
from Package.models import User

from .menu import show_profile


@dp.callback_query_handler(lambda call: call.data == "open_profile", state='*')
async def open_profile(call: CallbackQuery, state=FSMContext):

    current_state = await state.get_state()
    if current_state is not None:
        logger.debug(f"[{call.from_user.id}] open profile")
        await state.finish()

    await call.message.edit_caption(caption=texts.profile_text, reply_markup=await keyboard.profile_keyboard())


@dp.callback_query_handler(lambda call: call.data == "back_menu", state='*')
async def back_menu(call: CallbackQuery, state=FSMContext):

    current_state = await state.get_state()
    if current_state is not None:
        logger.debug(f"[{call.from_user.id}] back to menu")
        await state.finish()

    await call.message.edit_caption(caption=None, reply_markup=keyboard.panel_keyboard())


@dp.callback_query_handler(lambda call: call.data == "back_menu_categories", state='*')
async def back_menu(call: CallbackQuery, state=FSMContext):

    current_state = await state.get_state()
    if current_state is not None:
        logger.debug(f"[{call.from_user.id}] back to menu")
        await state.finish()
    with open('data/media/menu.jpg', 'rb') as pic:
        media = InputMediaPhoto(media=pic)
        await call.message.edit_media(media=media)
        await call.message.edit_caption(caption=None, reply_markup=keyboard.panel_keyboard())


@dp.callback_query_handler(lambda call: call.data.startswith("close_btn"))
async def close_btn(call: CallbackQuery):
    await call.message.edit_caption(caption=None, reply_markup=await keyboard.choose_category_key())
