from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


menu_keyboard = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
menu_btn = KeyboardButton('Главное меню ✈️')
about_btn = KeyboardButton('О проекте ℹ️')
menu_keyboard.add(menu_btn)
menu_keyboard.add(about_btn)
menu_keyboard.input_field_visibility = True
menu_keyboard.input_field_placeholder = '✈️ AI Travel'


def panel_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton('👨‍💻 Профиль', callback_data='open_profile')
    btn2 = InlineKeyboardButton('🔍 Найти отель', callback_data='search_hotel')
    btn3 = InlineKeyboardButton('📍 Категория мест', callback_data='request_location')
    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)

    return markup


async def profile_keyboard():
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('❤️ Избранное', callback_data='favourites'),
         InlineKeyboardButton('⚙️ Настройки', callback_data='settings')],
        [InlineKeyboardButton('◀️ Назад', callback_data='back_menu')]
    ])
    return markup


def registration_btn() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton('Продолжить ➡️', callback_data="return_reg")
    markup.add(btn1)

    return markup


def phone_info() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton('📲', callback_data="request_phone")
    markup.add(btn)

    return markup


async def share_phone_button():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = KeyboardButton(text='📲', request_contact=True)
    markup.add(button)
    return markup


async def choose_category_key():
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('🏛 Музеи', callback_data='category_museum'),
         InlineKeyboardButton('🍿 Кинотеатры', callback_data='category_cinema')],
        [InlineKeyboardButton('🍽 Рестораны', callback_data='category_restaurant'),
         InlineKeyboardButton('🏨 Отели', callback_data='category_hotel')],
        [InlineKeyboardButton('◀️ Назад', callback_data='back_menu_categories')]
    ])
    return markup


async def location_keyboard():
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('🌍 Отправить локацию',
                              callback_data='send_location')]])
    return markup


async def location_button():
    button_text = '🌍 Отправить локацию'
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = KeyboardButton(text=button_text, request_location=True)
    markup.add(button)
    return markup


async def request_location() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Обновить геопозицию 🔄', callback_data='send_location')],
        [InlineKeyboardButton('Продолжить ➡️', callback_data='category_places')]
    ])
    return markup


def back_btn() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton('◀️', callback_data="back_menu")
    markup.add(btn)

    return markup