from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from loguru import logger

from loader import dp, config, status_names
from data import texts, keyboard
from Package.models import User

from .menu import show_menu


@dp.message_handler(
    Text(startswith="Главное меню", ignore_case=True), is_user=True, state="*"
)
async def main_menu(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        logger.debug(f"Cancelling state {current_state} in bot menu")
        await state.finish()
    chat_id = message.from_user.id
    await show_menu(chat_id)


@dp.message_handler(
    Text(startswith="О проекте", ignore_case=True), is_user=True, state="*"
)
async def about_project(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        logger.debug(f"Cancelling state {current_state} in about project")
        await state.finish()
