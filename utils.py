"""
Полезные утилиты для фомирования лог-параметров
"""

import multiprocessing
import socket

from os import getenv

from rest_framework import status


# Уровень логирования в системе
DJANGO_LOG_LEVEL = getenv('DJANGO_LOG_LEVEL', 'DEBUG')

# Уровень логирования для CEF-логов
CEF_LOG_LEVEL = getenv('DJANGO_LOG_LEVEL', 'DEBUG')


class ExternalCounter:
    """
    Класс для расчета лог-параметра externalId на основе AtomicInteger.
    """

    def __init__(self, external_value=0):
        self._external_value = int(external_value)
        self._lock = multiprocessing.Lock()

    def __call__(self, *args, **kwargs):
        return self.external_increment()

    def external_increment(self, step=1):
        """
        Метод для увеличения значения external_id.

        Args:
            step (int): значение, на которое увеличивается external_id

        Returns:
            external_value (int): новое значение external_id
        """
        with self._lock:
            self._external_value += int(step)
            return self._external_value

    @property
    def external_value(self):
        with self._lock:
            return self._external_value

    @external_value.setter
    def external_value(self, new_value):
        with self._lock:
            self._external_value = int(new_value)
            return self._external_value


class LogLevels:
    """
    Уровни логирования в системе.
    """

    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4

    @classmethod
    def is_debug(cls):
        """
        Проверка уровня логирования DEBUG.
        """
        return cls.DEBUG >= getattr(cls, DJANGO_LOG_LEVEL, cls.DEBUG)

    @classmethod
    def is_info(cls):
        """
        Проверка уровня логирования INFO.
        """
        return cls.INFO >= getattr(cls, DJANGO_LOG_LEVEL, cls.DEBUG)

    @classmethod
    def is_warning(cls):
        """
        Проверка уровня логирования WARNING.
        """
        return cls.WARNING >= getattr(cls, DJANGO_LOG_LEVEL, cls.DEBUG)

    @classmethod
    def is_error(cls):
        """
        Проверка уровня логирования ERROR.
        """
        return cls.ERROR >= getattr(cls, DJANGO_LOG_LEVEL, cls.DEBUG)

    @classmethod
    def is_critical(cls):
        """
        Проверка уровня логирования CRITICAL.
        """
        return cls.CRITICAL >= getattr(cls, DJANGO_LOG_LEVEL, cls.DEBUG)

    @classmethod
    def is_cef_level(cls):
        """
        Проверка уровня логирования для публикации CEF-логов.
        """
        return getattr(cls, CEF_LOG_LEVEL, cls.DEBUG) >= getattr(cls, DJANGO_LOG_LEVEL, cls.DEBUG)


class Outcomes:
    """
    Класс c информацией о лог-параметре outcome.
    """

    failure: str = 'failure'
    success: str = 'success'
    reason: str = 'reason'
    outcome: str = 'outcome'
    outcomes: tuple = (failure, success)

    @classmethod
    def get_outcome(cls, response=None, error=None):
        """
        Получение словаря outcome на основе response.
        """
        if error:
            return {cls.outcome: cls.failure, cls.reason: error}
        if not status.is_success(response.status_code):
            return {cls.outcome: cls.failure, cls.reason: response.data}
        return {cls.outcome: cls.success, cls.reason: 'None'}


class LogLabels:
    """
    Наименования для Labels.
    """

    new_value = 'Новое значение'
    old_value = 'Старое значение'
    attribute_name = 'Наименование атрибута'
    object_name = 'Наименование объекта'


class SeverityLevels:
    """
    Уровни важности события.
    """

    SEVERITY_LEVEL_1 = 1
    SEVERITY_LEVEL_2 = 2
    SEVERITY_LEVEL_3 = 3
    SEVERITY_LEVEL_4 = 4
    SEVERITY_LEVEL_5 = 5
    SEVERITY_LEVEL_6 = 6
    SEVERITY_LEVEL_7 = 7
    SEVERITY_LEVEL_8 = 8
    SEVERITY_LEVEL_9 = 9
    SEVERITY_LEVEL_10 = 10


class RESTMethods:
    """
    Наименования методов запроса.
    """

    GET = 'GET'
    POST = 'POST'
    PATCH = 'PATCH'
    PUT = 'PUT'
    DELETE = 'DELETE'
    HEAD = 'HEAD'
    OPTION = 'OPTION'

    class Severity:
        """
        Уровень важности в зависимости от метода запроса.
        """

        HEAD = SeverityLevels.SEVERITY_LEVEL_3
        OPTION = SeverityLevels.SEVERITY_LEVEL_3
        GET = SeverityLevels.SEVERITY_LEVEL_3
        POST = SeverityLevels.SEVERITY_LEVEL_6
        PATCH = SeverityLevels.SEVERITY_LEVEL_6
        PUT = SeverityLevels.SEVERITY_LEVEL_6
        DELETE = SeverityLevels.SEVERITY_LEVEL_8

    class DeviceEventClassID:
        """
        Тип события в зависимости от метода запроса.
        """

        GET = 'view'
        PATCH = PUT = 'update'
        POST = 'create'
        DELETE = 'delete'

    class Message:
        """
        Дефолтное msg в зависимости от метода запроса.
        """

        GET = 'Просмотр объекта'
        PATCH = PUT = 'Объект изменен'
        POST = 'Создан объект'
        DELETE = 'Удален объект'

    def is_cef_method(self, method):
        """
        Отношение метода к CEF-событиям.
        """
        return self.is_modifying_method(method) or method == self.POST

    def is_modifying_method(self, method):
        """
        Методы, изменяющие существующий объект в системе.
        """
        return method in (self.PUT, self.PATCH, self.DELETE)


def get_request_user(request):
    """
    Получение пользователя из request.
    """
    try:
        return request.user.profile.full_name
    except Exception as error:
        return error


def get_required_log_attributes(request):
    """
    Метод для формирования словаря атрибутов из request.

    Returns:
        dict(dict): словарь с атрибутами для логов

    """
    return {
        'DeviceEventClassID': getattr(RESTMethods.DeviceEventClassID, request.method, 'base'),
        'Name': request.resolver_match.view_name,
        'Severity': getattr(RESTMethods.Severity, request.method, RESTMethods.Severity.GET),
        'externalId': external_counter(),
        'shost': request.get_host(),
        'src': visitor_ip_address(request),
        'suser': get_request_user(request),
        'dhost': get_dhost(request),
        'dst': get_dst(),
    }


def get_dhost(request):
    """Метод для получения адреса назначения из request.

    Args:
        request (Request): объект запроса WSGI

    Returns:
        str: строка с адресом назначения
    """
    host = request.META.get('HTTP_HOST', '')
    path_info = request.META.get('PATH_INFO', '')
    return ''.join([host, path_info]) if host and path_info else ''


def get_dst():
    """Метод для получения IP-адреса сервера

    Returns:
        str: строка с IP-адреса сервера
    """
    return socket.gethostbyname(socket.gethostname())


def visitor_ip_address(request):
    """Метод для формирования значения IP-адреса из request.

    Args:
        request (Request): объект запроса WSGI

    Returns:
        IP (str): IP-адрес

    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip if ip else '127.0.0.1'


# экземпляр класса для расчета атрибута externalId
external_counter = ExternalCounter()

# экземпляр класса для расчета атрибута externalId в АМ
am_external_counter = ExternalCounter()
