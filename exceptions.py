"""Модуль исключений."""


class BaseEnvError(Exception):
    """Вызывается при ошибках переменных окружения."""


class GetAnswerFromAPIError(Exception):
    """Ошибка получения ответа от API."""


class SendMessageError(Exception):
    """Выбрасывается при ошибке отправки сообщения."""
