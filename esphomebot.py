from http import HTTPStatus
import json
import logging
from logging import StreamHandler
import os
import requests
import sys
import time

from dotenv import load_dotenv
from telebot import TeleBot
from telebot.apihelper import ApiException

from exceptions import (
    BaseEnvError,
    GetAnswerFromAPIError,
    SendMessageError
)


RETRY_PERIOD = 600

logger = logging.getLogger('ESPHome_Bot')
formatter = logging.Formatter(
    '%(asctime)s: [%(levelname)s] %(funcName)s line %(lineno)d  %(message)s'
)
logger.setLevel(logging.DEBUG)
handler = StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)


class ESPHomeBot:
    """
    Класс бота для общения с ESPHome.
    Пока ничего не умеет)).
    """

    def __init__(self) -> None:
        """
        Инициализируем переменные окружения и эндпоинты.
        """
        load_dotenv()

        self.TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
        self.TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
        self.BASE_NAME = 'http://esptemppres.local/sensor/'
        self.ENDPOINTS = [
            'bmp280_pres',
            'bmp280_temp',
            'dallas_temp_1',
            'dallas_temp_2',
            'dht_temp',
            'dht_hum',
        ]
        self.check_tokens()
        self.bot = TeleBot(token=self.TELEGRAM_TOKEN)

    def check_tokens(self):
        """
        Проверка токенов.

        Осуществляет проверку токенов к API Практикума и Telegram-боту,
        а также наличие ID чата с пользователем.
        В случае их отсутсвия вызываются исключение BaseEnvError.

        Args:
            None

        Returns:
            None
        """
        tokens = {
            'TELEGRAM_TOKEN': self.TELEGRAM_TOKEN,
            'TELEGRAM_CHAT_ID': self.TELEGRAM_CHAT_ID
        }
        error_msg = ''
        for token_name, token_value in tokens.items():
            if token_value is None:
                error_msg += f'Отсутсвует переменная окружения {token_name}.\n'
        if error_msg != '':
            logger.critical(error_msg, exc_info=True)
            raise BaseEnvError(error_msg)
        logger.debug('Переменные окружения в порядке.')

    def send_message(self, message):
        """
        Отправка сообщения.

        Отправляет сообщение через бота.
        Отправляет в лог сообщение об отправке.
        В случае ошибки отправки сообщения выбрасывает исключение
        SendMessageError.

        Args:
            bot (TeleBot): экземпляр бота.
            message (str): строка сообщения.

        Returns:
            None
        """
        try:
            self.bot.send_message(chat_id=self.TELEGRAM_CHAT_ID, text=message)
        except ApiException as error:
            error_msg = f'Ошибка отправки сообщения: {error}'
            raise SendMessageError(error_msg)
        else:
            logger.debug(f'Сообщение отправлено: {message}')
        return True

    def get_api_answer(self):
        """
        Получение ответа от API ESPHome.

        Осуществляет запрос к API ESPHome.
        В случае ошибок получения ответа вызывает исключение
        GetAnswerFromAPIError.

        Returns:
            (dict): Объект json, приведенный к типам Python
        """
        self.results = []
        bn = self.BASE_NAME
        for endpoint in self.ENDPOINTS:
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
                self.results.append(response.json())
            except json.JSONDecodeError as error:
                error_msg = f'Не валидный JSON: {error}'
                raise GetAnswerFromAPIError(error_msg)

    def send_answer(self):
        """
        Отсылает ответ от API ESPHome.
        Все ответы от эндпоинтов отсылаются в телеграм.
        """
        message = ''
        for result in self.results:
            id = result.get('id')
            state = result.get('state')
            message += f'{id} = {state}\n'
        self.send_message(message)


def main():
    """Основная логика работы бота."""
    EHbot = ESPHomeBot()
    while True:
        try:
            EHbot.get_api_answer()
            EHbot.send_answer()
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message, exc_info=True)
            EHbot.send_message(message)
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
