import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telegram.Bot(TELEGRAM_TOKEN)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(
    handlers=[logging.StreamHandler()],
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    try:
        if homework_status == 'reviewing':
            verdict = 'Работа взята в ревью'
        elif homework_status == 'rejected':
            verdict = 'К сожалению, в работе нашлись ошибки.'
        else:
            verdict = 'Ревьюеру всё понравилось, работа зачтена!'
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    except requests.RequestException as e:
        raise ConnectionError(
            logging.error(e, exc_info=True),
            print(f'Неверный ответ сервера: {e}'))


def get_homeworks(current_timestamp):
    URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses'
    if current_timestamp is None:
        current_timestamp = time or None
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(URL, headers=headers, params=payload)
        return homework_statuses.json()
    except requests.RequestException as e:
        raise ConnectionError(
            logging.error(e, exc_info=True),
            print(f'Неверный ответ сервера: {e}'))


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            try_get_homework = get_homeworks(current_timestamp)
            if try_get_homework.get('homeworks'):
                send_message(
                    parse_homework_status(
                        try_get_homework.get('homeworks')[0]))
            current_timestamp = try_get_homework.get('current_date')
            time.sleep(5 * 60)
        except Exception as e:
            logging.error(e, exc_info=True)
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
