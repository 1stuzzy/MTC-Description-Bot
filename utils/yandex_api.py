import aiohttp
import math
import time

from loguru import logger
from loader import config

from yandex_reviews_parser.utils import YandexParser


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance


async def get_places(lat, lon, category):
    radius = config.radius_limit

    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise ValueError(logger.exception("Invalid coordinates"))

    url = f"https://search-maps.yandex.ru/v1/?apikey={config.ya_token}&text={category}&lang=ru_RU&ll={lon},{lat}&spn=0.1,0.1&results={config.request_limit}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(logger.exception(f"Failed to get data: {response.status}"))

            data = await response.json()
            places = []
            for feature in data.get('features', []):
                coordinates = feature['geometry']['coordinates']
                distance_km = calculate_distance(lat, lon, coordinates[1], coordinates[0])
                if distance_km <= radius:
                    properties = feature.get('properties', {})
                    company_metadata = properties.get('CompanyMetaData', {})
                    id_company = company_metadata.get('id')
                    name = properties.get('name')
                    address = properties.get('description')

                    places.append({
                        'pid': id_company,
                        'name': name,
                        'address': address,
                        'distance_km': distance_km,
                        'lat': coordinates[1],
                        'lon': coordinates[0]
                    })

            return places


def get_company_rating(pid):
    parser = YandexParser(pid)
    company_data = parser.parse(type_parse='company')
    rating = company_data.get('company_info', {}).get('rating', 0)

    # Если рейтинг равен 0, возвращаем "Без рейтинга"
    if rating == 0:
        return "Без рейтинга"

    return rating

