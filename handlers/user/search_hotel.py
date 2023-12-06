from time import time

from aiogram import types
from aiogram.types import InputMediaPhoto, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from loader import dp
from data import keyboard, texts
from data.states import SearchHotels
from utils import basefunctional
from utils.function import create_description


@dp.callback_query_handler(lambda call: call.data == "search_hotel", state='*')
async def search_hotel(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer('<b>✍️ Введите название отеля:</b>')
    await SearchHotels.hotel_name.set()


@dp.message_handler(state=SearchHotels.hotel_name)
async def enter_hotel_name(message: types.Message, state: FSMContext):
    hotel_name = message.text
    await state.update_data(hotel_name=hotel_name)
    await message.answer('<b>✍️ Теперь введите название города:</b>')
    await SearchHotels.city_name.set()


@dp.message_handler(state=SearchHotels.city_name)
async def enter_city_name(message: types.Message, state: FSMContext):
    city_name = message.text
    await state.update_data(city_name=city_name)

    user_data = await state.get_data()
    hotel_name = user_data['hotel_name']
    hotel_city = user_data['city_name']

    await message.answer("Поиск отеля...")
    hotel_id = await basefunctional.find_hotel(hotel_name, hotel_city)

    if hotel_id is None:
        await message.answer("Отель не найден. Пожалуйста, попробуйте снова.")
        await state.finish()
        return

    await message.answer("Отель найден. Проверяю наличие отзывов...")
    desc = create_description(hotel_id)

    if desc == "Отзывы не найдены.":
        await message.answer("Отзывы не найдены. Начинаю парсить отзывы...")
    else:
        await message.answer("Отзывы найдены. Формирую описание...")
        await message.answer("Отправляю информацию в Chat GPT для создания описания...")

    await basefunctional.update_description(hotel_id, desc)
    await message.answer(f"Описание для отеля {hotel_name}:\n\n{desc}")
    await state.finish()
