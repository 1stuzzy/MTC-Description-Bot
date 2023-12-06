from loguru import logger

from Package.models import User, Place, ReviewLink


def create_user(chat_id: int, username: str, name: str, phone_number: int):
    return User.create(cid=chat_id, username=username, name=name, phone=phone_number)


def set_status(user_cid: int, status: int):
    try:
        user = User.get(cid=user_cid)
        user.status = status
        user.send_summary = True
        user.save()
    except User.DoesNotExist:
        pass


def save_place(place_info):
    try:
        existing_place = Place.get_or_none(Place.name == place_info['name'], Place.address == place_info['address'])
        if not existing_place:
            Place.create(
                name=place_info['name'],
                address=place_info['address'],
                description=place_info.get('description', ''),
                category=place_info.get(''),
                latitude=place_info.get('latitude'),
                longitude=place_info.get('longitude'),
            )
    except Exception as e:
        logger.error(f"Error saving place: {e}")


async def find_hotel(name, city):
    try:
        hotel = Place.select().where((Place.name == name) & (Place.address.contains(city))).get()
        return hotel.pid
    except Place.DoesNotExist:
        return None


async def update_description(pid, description):
    query = Place.update(description=description).where(Place.pid == pid)
    query.execute()


def save_review_link(pid, url):
    if not reviews_exists(pid):
        place = Place.get(Place.pid == pid)
        ReviewLink.create(place=place, url=url)


def reviews_exists(pid):
    try:
        exists = ReviewLink.select().join(Place).where(Place.pid == pid).exists()
        return exists
    except ReviewLink.DoesNotExist:
        return False


def get_reviews(pid):
    try:
        review_link = ReviewLink.select().join(Place).where(Place.pid == pid).get()
        return review_link.url  # Возвращает URL, если запись найдена
    except ReviewLink.DoesNotExist:
        return None  # Возвращает None, если записи нет
