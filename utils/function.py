import requests
import httpx
from bs4 import BeautifulSoup
from yandex_reviews_parser.utils import YandexParser
from telegraph import Telegraph

from loguru import logger
from Package.models import Place
from utils.basefunctional import save_review_link, reviews_exists, get_reviews
from loader import config


from langchain.schema import HumanMessage
from langchain.chat_models.gigachat import GigaChat


def parse_reviews(pid):
    logger.info(f"Парсинг отзывов для отеля с PID: {pid}")
    parser = YandexParser(pid)
    reviews_data = parser.parse(type_parse='reviews')
    extracted_reviews = []

    if 'company_reviews' in reviews_data:
        five_star_reviews = [review for review in reviews_data['company_reviews'] if review.get('stars', 0) == 5]
        four_star_reviews = [review for review in reviews_data['company_reviews'] if review.get('stars', 0) == 4]

        extracted_reviews = five_star_reviews[:35]
        remaining_slots = 35 - len(extracted_reviews)
        if remaining_slots > 0:
            extracted_reviews.extend(four_star_reviews[:remaining_slots])

        all_ratings = [review.get('stars', 0) for review in reviews_data['company_reviews']]
        average_rating = sum(all_ratings) / len(all_ratings) if all_ratings else None

        return average_rating, extracted_reviews

    return None, []


def create_url(pid, reviews_data):
    average_rating, reviews = reviews_data
    logger.info(f"Создание страницы на Telegraph для отеля с PID: {pid}")

    try:
        hotel_name = Place.get(Place.pid == pid).name
    except Place.DoesNotExist:
        logger.error(f"Отель с ID {pid} не найден.")
        return

    telegraph = Telegraph()
    telegraph.create_account(short_name='Workers')

    content = [{"tag": "h4", "children": [f"Отзывы об отеле {hotel_name}"]}]
    content.append({"tag": "p", "children": [f"Общий рейтинг: {average_rating:.2f} звезд"]})
    for review in reviews:
        content.append({"tag": "p", "children": [f"{review['text']}"]})

    try:
        response = telegraph.create_page(
            title=f"Отзывы об отеле {hotel_name}",
            author_name="HotelReviews",
            content=content
        )
        url = response.get('url')
        logger.info(f"Telegraph страница создана: {url}")
        return url
    except Exception as e:
        logger.error(f"Ошибка при создании страницы: {e}")


def create_url2(pid, reviews):
    logger.info(f"Создание страницы на Telegraph для отеля с PID: {pid}")
    try:
        hotel_name = Place.get(Place.pid == pid).name
    except Place.DoesNotExist:
        print(f"Отель с ID {pid} не найден.")
        return

    telegraph = Telegraph()
    telegraph.create_account(short_name='Workers')

    content = [{"tag": "h4", "children": [f"Отзывы об отеле {pid}"]}]
    for review in reviews:
        content.append({"tag": "p", "children": [f"Рейтинг: {review['stars']} звезд"]})
        content.append({"tag": "p", "children": [review['text']]})

    try:
        response = telegraph.create_page(
            title=f"Отзывы об отеле {hotel_name}",
            author_name="HotelReviews",
            content=content
        )
        url = response.get('url')
        logger.info(f"Telegraph страница создана: {url}")
        return url
    except Exception as e:
        logger.error(f"Ошибка при создании страницы: {e}")


def send_post_gpt(url):
    logger.info(f"Отправка запроса на Yandex GPT для URL: {url}")
    endpoint = 'https://300.ya.ru/api/sharing-url'
    headers = {'Authorization': f'OAuth {config.gpt_token}'}
    payload = {'article_url': url}

    response = requests.post(endpoint, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get('sharing_url')  # Убедитесь, что это правильный ключ
    else:
        logger.error(f'Ошибка запроса: {response.status_code}')
        return None


def export_url_text(url):
    logger.info(f"Экспорт текста из URL: {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.content.decode('utf-8'), 'html.parser')

    paragraphs = soup.find_all('p')
    text = ""
    for paragraph in paragraphs:
        if "У сервиса есть REST-образный интерфейс" not in paragraph.get_text():
            if "в них могут быть ошибки и неточности" not in paragraph.get_text():
                text += paragraph.get_text() + "\n"

    return text


def create_description(pid):
    logger.info(f"create_description: {pid}")

    saved_review_url = reviews_exists(pid)
    if saved_review_url:
        logger.info(f"Using saved review link for hotel with PID: {pid}")
        telegraph_url = get_reviews(pid)
    else:
        reviews = parse_reviews(pid)
        if not reviews:
            return "Отзывы не найдены."

        telegraph_url = create_url(pid, reviews)
        if telegraph_url:
            save_review_link(pid, telegraph_url)
        if not telegraph_url:
            logger.error("Не удалось создать страницу на Telegraph.")
            return "Не удалось создать страницу на Telegraph."

    review_text = export_url_text(telegraph_url)
    if not review_text:
        logger.error("Не удалось получить текст отзывов.")
        return "Не удалось получить текст отзывов."

    description = optimized_description(review_text)
    if not description:
        logger.error("Не удалось сгенерировать описание через GPT.")
        return "Не удалось сгенерировать описание через GPT."

    return description


def optimized_description2(reviews):
    try:
        logger.info(f"Sending the following data to GPT-3: {reviews}")
        proxy_url = "http://vPQHEs7x:2KqFxZEa@154.194.76.115:63032"
        proxies = {
            "http://": proxy_url,
            "https://": proxy_url
        }

        with httpx.Client(proxies=proxies, timeout=60.0) as client:
            response = client.post(
                "https://api.openai.com/v1/engines/text-davinci-003/completions",
                json={
                    "prompt": f"Создайте вдохновляющее и исключительно положительное описание отеля Резидент, опираясь на отзывы {reviews}"
                              f"Игнорируйте любые негативные комментарии или аспекты.",
                              "max_tokens": 2040
                },
                headers={
                    "Authorization": "Bearer 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"
                }
            )
        response.raise_for_status()
        return response.json()['choices'][0]['text'].strip()
    except Exception as e:
        logger.error(f"Ошибка при генерации описания через GPT: {e}")
        return None


def optimized_description3(reviews):
    try:
        logger.info(f"Sending the following data to GigaChat: {reviews}")

        # Создайте экземпляр GigaChat
        chat = GigaChat(credentials='52815fac-46ee-41de-9940-ee513d9c2417', verify_ssl_certs=False)

        # Создайте сообщение для отправки в GigaChat
        user_message = HumanMessage(content=f"Создайте вдохновляющее и исключительно положительное описание отеля Резидент, опираясь на отзывы {reviews}. Игнорируйте любые негативные комментарии или аспекты.")

        # Отправьте сообщение и получите ответ
        response = chat([user_message])

        if response and response.content:
            return response.content
        else:
            logger.error("Ответ от GigaChat не содержит текста.")
            return None
    except Exception as e:
        logger.error(f"Ошибка при генерации описания через GigaChat: {e}")
        return None


def optimized_description(reviews):
    url = "https://api.ai21.com/studio/v1/j2-ultra/chat"

    payload = {
        "numResults": 1,
        "temperature": 0.3,
        "messages": [
            {
                "text": reviews,
                "role": "user"
            }
        ],
        "system": "Создайте вдохновляющее и исключительно положительное описание отеля Резидент, опираясь на отзывы. Игнорируйте любые негативные комментарии или аспекты."
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {config.ai_token}"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        # Извлекаем текст из первого элемента массива 'outputs'
        return response_data['outputs'][0]['text']
    except Exception as e:
        print(f"Ошибка при генерации описания отеля: {e}")
        return None
