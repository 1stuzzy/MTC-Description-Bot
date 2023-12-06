from aiogram.dispatcher.filters.state import StatesGroup, State


class SearchHotels(StatesGroup):
    hotel_name = State()
    city_name = State()