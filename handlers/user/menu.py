from loader import dp
from data import keyboard, texts

from Package.models import User


async def show_menu(chat_id):
    await dp.bot.send_message(chat_id, texts.airplane_smile, reply_markup=keyboard.menu_keyboard)
    with open('data/media/menu.jpg', 'rb') as pic:
        await dp.bot.send_photo(chat_id, pic, caption=None, reply_markup=keyboard.panel_keyboard())


async def show_profile(chat_id):
    await dp.bot.send_message(chat_id, texts.worker_smile, reply_markup=keyboard.menu_keyboard)
    with open('data/media/menu.jpg', 'rb') as pic:
        await dp.bot.send_photo(chat_id, pic, caption=None, reply_markup=await keyboard.profile_keyboard())
