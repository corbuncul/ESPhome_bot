class BaseEnvError(Exception):
    """Вызывается при ошибках переменных окружения."""

    pass


class GetAnswerFromAPIError(Exception):
    """Ошибка получения ответа от API."""

    pass


class SendMessageError(Exception):
    """Выбрасывается при ошибке отправки сообщения."""

    pass
