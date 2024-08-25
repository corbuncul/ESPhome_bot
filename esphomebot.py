from http import HTTPStatus
import json
import logging
from logging import StreamHandler
import os
import requests
import sys

from dotenv import load_dotenv
from telebot import TeleBot, types

from exceptions import (
    BaseEnvError,
    GetAnswerFromAPIError,
)


logger = logging.getLogger('ESPHome_Bot')
formatter = logging.Formatter(
    '%(asctime)s: [%(levelname)s] %(funcName)s line %(lineno)d  %(message)s'
)
logger.setLevel(logging.DEBUG)
handler = StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
BASE_NAME = 'http://esptemppres.local/sensor/'
ENDPOINTS = [
    'bmp280_pres',
    'bmp280_temp',
    'dallas_temp_1',
    'dallas_temp_2',
    'dht_temp',
    'dht_hum',
]
HELP_MESSAGE = (
    'Привет! Я бот, который выступает посредником между ESPHome и тобой.\n'
    'В ответ на команды, я запрашиваю данные с ESPHome и оправляю ответ тебе.'
)


def check_tokens():
    """
    Проверка токенов.

    Осуществляет проверку токенов Telegram-боту,
    а также наличие ID чата с пользователем.
    В случае их отсутсвия вызываются исключение BaseEnvError.

    Args:
        None

    Returns:
        None
    """
    tokens = {
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }
    error_msg = ''
    for token_name, token_value in tokens.items():
        if token_value is None:
            error_msg += f'Отсутсвует переменная окружения {token_name}.\n'
    if error_msg != '':
        logger.critical(error_msg, exc_info=True)
        raise BaseEnvError(error_msg)
    logger.debug('Переменные окружения в порядке.')


def check_boss_id(message):
    """Проверка на владельца бота."""
    return message.chat.id == int(TELEGRAM_CHAT_ID)


def get_api_answer():
    """
    Получение ответа от API ESPHome.

    Осуществляет запрос к API ESPHome.
    В случае ошибок получения ответа вызывает исключение
    GetAnswerFromAPIError.

    Returns:
        (dict): Объект json, приведенный к типам Python
    """
    results = []
    bn = BASE_NAME
    for endpoint in ENDPOINTS:
        logger.debug(f'Соединение с {bn+endpoint}')
        try:
            response = requests.get(bn + endpoint)
        except requests.RequestException as error:
            error_msg = f'Ошибка соединения с API: {error}'
            raise GetAnswerFromAPIError(error_msg)

        status_code = response.status_code
        if status_code != HTTPStatus.OK:
            error_msg = f'Ошибка ответа HTTP status: {status_code}'
            raise GetAnswerFromAPIError(error_msg)

        logger.debug(f'Получен ответ от {bn+endpoint}')

        try:
            results.append(response.json())
        except json.JSONDecodeError as error:
            error_msg = f'Не валидный JSON: {error}'
            raise GetAnswerFromAPIError(error_msg)
    return results


def make_tg_answer(results):
    """Подготавливает ответ от API ESPHome."""
    msg = ''
    for result in results:
        id = result.get('id')[7:]
        state = result.get('state')
        msg += f'{id} = {state}\n'
    return msg


check_tokens()
bot = TeleBot(token=TELEGRAM_TOKEN)


@bot.message_handler(commands=['start'])
def wake_up(message):
    """
    Функция приветствия.
    В ответ на команду /start
    отправляет сообщение приветственное сообщение.
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_start = types.KeyboardButton('/start')
    keyboard.add(button_start)
    button_sensors = types.KeyboardButton('/sensors')
    keyboard.add(button_sensors)
    if message.chat.id == int(TELEGRAM_CHAT_ID):
        button_settings = types.KeyboardButton('/settings')
        keyboard.add(button_settings)

    bot.send_message(
        chat_id=message.chat.id,
        text=HELP_MESSAGE,
        reply_markup=keyboard,
    )


@bot.message_handler(commands=['sensors'])
def sensors_data(message):
    """Отправка данных с сенсоров в телеграм."""
    try:
        bot.send_message(
            chat_id=message.chat.id,
            text=make_tg_answer(get_api_answer())
        )
    except GetAnswerFromAPIError as e:
        bot.send_message(
            chat_id=message.chat.id,
            text=f'Ошибка получения данных: {e}'
        )


@bot.message_handler(func=check_boss_id, commands=['settings'])
def set_settings(message):
    """Заготовка на будущее."""
    bot.send_message(chat_id=message.chat.id, text='Тут пока ничего нет.')


bot.infinity_polling()
