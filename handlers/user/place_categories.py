from time import time

from aiogram import types
from aiogram.types import InputMediaPhoto, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from loader import dp
from data import keyboard, texts
from loguru import logger

from Package.models import User, Place
from utils.yandex_api import get_places, get_company_rating
places_cache = {}


@dp.callback_query_handler(lambda c: c.data == 'request_location')
async def request_location(c: types.CallbackQuery):
    user_id = c.from_user.id

    with open('data/media/ava.png', 'rb') as pic:
        media = InputMediaPhoto(media=pic)
        await dp.bot.edit_message_media(chat_id=user_id, message_id=c.message.message_id, media=media)

    await dp.bot.edit_message_caption(chat_id=user_id, message_id=c.message.message_id,
                                      caption=texts.choose_movement, reply_markup=await keyboard.request_location())


@dp.callback_query_handler(lambda c: c.data == 'send_location')
async def send_location_callback(c: types.CallbackQuery):
    user_id = c.from_user.id

    with open('data/media/location.png', 'rb') as pic:
        media = InputMediaPhoto(media=pic)
        await dp.bot.edit_message_media(chat_id=user_id, message_id=c.message.message_id, media=media)

    await dp.bot.edit_message_caption(chat_id=user_id, message_id=c.message.message_id,
                                      caption=texts.share_location_text)

    await dp.bot.send_sticker(chat_id=user_id,
                              sticker='CAACAgIAAxkBAAEKlKNlNZkLB0CHR9B8FnxG9mCEmXWOuAACCgwAAoSteUp4qnHL4LRiODAE',
                              reply_markup=await keyboard.location_button())


@dp.message_handler(content_types=types.ContentType.LOCATION)
async def updating_location(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = User.get(cid=user_id)

    # Обновляем местоположение пользователя
    latitude = message.location.latitude
    longitude = message.location.longitude
    user.latitude = latitude
    user.longitude = longitude
    user.save()

    await message.answer(texts.location_smile, reply_markup=keyboard.menu_keyboard)
    with open('data/media/map.png', 'rb') as pic:
        await message.answer_photo(photo=pic, caption="Выберите категорию:", reply_markup=await keyboard.choose_category_key())


@dp.callback_query_handler(lambda call: call.data == "category_places", state='*')
async def categories(call: CallbackQuery, state=FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        logger.debug(f"Cancelling state {current_state} in bot category places")
        await state.finish()

    user_id = call.from_user.id
    user = User.get(cid=user_id)

    if not user.latitude or not user.longitude:
        await call.answer(texts.invalid_location_text, show_alert=True)
        await call.message.edit_reply_markup(reply_markup=await keyboard.location_keyboard())
        return
    else:
        with open('data/media/map.png', 'rb') as pic:
            media = InputMediaPhoto(media=pic)
            await dp.bot.edit_message_media(chat_id=user_id, message_id=call.message.message_id, media=media)
            await call.message.edit_reply_markup(reply_markup=await keyboard.choose_category_key())


DELTA = 0.0001
ITEMS_PER_PAGE = 5


@dp.callback_query_handler(lambda c: c.data.startswith("category_"))
async def show_recommended_places(c: types.CallbackQuery):
    user_id = c.from_user.id
    user = User.get(cid=user_id)
    category = c.data.split("_")[1]
    await dp.bot.send_chat_action(c.message.chat.id, action="find_location")
    places = await get_or_fetch_places(user.latitude, user.longitude, category)

    if not places:
        await c.message.answer(texts.places_notfound_text)
        return

    await send_places(user_id, places, 0, category)


async def get_or_fetch_places(latitude, longitude, category):
    places = Place.select().where(
        Place.category == category,
        Place.latitude.between(latitude - DELTA, latitude + DELTA),
        Place.longitude.between(longitude - DELTA, longitude + DELTA)
    )
    if not places.exists():
        new_places = await get_places(latitude, longitude, category)
        for place in new_places:
            pid = place.get('pid')
            existing_place = Place.get_or_none(Place.pid == pid)
            if not existing_place:
                rating_info = get_company_rating(pid)
                Place.create(
                    pid=pid,
                    name=place['name'],
                    address=place['address'],
                    category=category,
                    latitude=latitude,
                    longitude=longitude,
                    rating=rating_info
                )
            elif existing_place and existing_place.rating is None:
                existing_place.rating = get_company_rating(pid) if pid else None
                existing_place.save()

        places = Place.select().where(
            Place.category == category,
            Place.latitude.between(latitude - DELTA, latitude + DELTA),
            Place.longitude.between(longitude - DELTA, longitude + DELTA)
        )
    return places


async def send_places(user_id, places, page, category, message_id=None):
    a = time()
    category_title = texts.category_title.get(category)
    start_index = page * ITEMS_PER_PAGE
    paginated_places = places[start_index:start_index + ITEMS_PER_PAGE]

    keyboard = InlineKeyboardMarkup()
    for place in paginated_places:
        place_id = place.id if isinstance(place, Place) else place['id']
        place_name = place.name if isinstance(place, Place) else place['name']
        callback_data = f"place_details_{category}_{place_id}"
        keyboard.add(InlineKeyboardButton(place_name, callback_data=callback_data))

    keyboard = page_keyboard(keyboard, page, len(places), category)

    if message_id:
        await dp.bot.edit_message_reply_markup(chat_id=user_id, message_id=message_id, reply_markup=keyboard)
    else:
        await dp.bot.send_photo(chat_id=user_id, photo=open('data/media/map.png', 'rb'),
                                caption=texts.result_text.format(category_title=category_title), reply_markup=keyboard)
    time_to_do = time() - a
    logger.debug(f"send_places: {time_to_do}")


@dp.callback_query_handler(lambda c: c.data.startswith("page_"))
async def paginate_places(c: types.CallbackQuery):
    _, category, new_page = c.data.split('_')
    new_page = int(new_page)
    user_id = c.from_user.id
    user = User.get(cid=user_id)

    places = await get_or_fetch_places(user.latitude, user.longitude, category)
    await send_places(user_id, places, new_page, category, message_id=c.message.message_id)


def page_keyboard(keyboard, page, total_items, category):
    has_prev = page > 0
    has_next = (page + 1) * ITEMS_PER_PAGE < total_items

    if has_prev:
        row_buttons = [InlineKeyboardButton("◀️", callback_data=f"page_{category}_{page-1}")]
    else:
        row_buttons = [InlineKeyboardButton(" ", callback_data="none")]

    row_buttons.append(InlineKeyboardButton("❌", callback_data="close_btn"))

    if has_next:
        row_buttons.append(InlineKeyboardButton("▶️", callback_data=f"page_{category}_{page+1}"))
    else:
        row_buttons.append(InlineKeyboardButton(" ", callback_data="none"))

    keyboard.row(*row_buttons)
    return keyboard


@dp.callback_query_handler(lambda c: c.data.startswith("place_details_"))
async def place_details(c: types.CallbackQuery):
    data_parts = c.data.split("_")
    category = "_".join(data_parts[1:-1])
    place_id = int(data_parts[-1])

    user_id = c.from_user.id
    if place_id <= 0:
        await dp.bot.send_message(chat_id=user_id, text="Неверный идентификатор заведения.")
        return

    try:
        place = Place.get(Place.id == place_id)
        category_name = texts.category_title.get(place.category, place.category)
        await dp.bot.send_location(user_id, latitude=place.latitude, longitude=place.longitude)
        await dp.bot.send_message(chat_id=user_id, text=texts.place_info.format(
            name=place.name,
            address=place.address,
            category=category_name,
            rating=f'{"⭐" * int(place.rating)} <b><i>({place.rating})</i></b>'
        ))

        # if place.image_url:
        #     await dp.bot.send_photo(chat_id=user_id, photo=place.image_url, caption=place_info)
    except Place.DoesNotExist:
        await dp.bot.send_message(chat_id=user_id, text="Информация о заведении не найдена.")
