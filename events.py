"""
Класcы-события валидируют параметры и публикуют лог-сообщение.
Здесь переопределяются классы из библиотеки cef_logger под ваши особенности.
"""

import time

from typing import Any, Union

from pydantic import Field

from cef_logger import Event
from cef_logger.fields import Fields
from cef_logger.schemas import ExtensionFields, MandatoryFields

from .utils import LogLevels


class CustomExtensionFields(ExtensionFields):
    """
    Переопределение типов полей из ExtensionFields.
    """

    dhost: Union[str, None] = Field(default=None, max_length=1023)
    dst: Union[str, None] = Field(default=None, max_length=1023)
    shost: Union[str, None] = Field(default=None, max_length=1023)
    suid: Union[str, None] = Field(default=None, max_length=1023)
    reason: Any = Field(default=None)
    cs1: Any = Field(default=None)
    cs2: Any = Field(default=None)
    cs3: Any = Field(default=None)
    cs4: Any = Field(default=None)
    cs5: Any = Field(default=None)
    cs6: Any = Field(default=None)
    externalId: Union[int, str, None] = Field(default=None)
    end: Any = Field(default=None)


class CustomFields(Fields):
    """
    Переопределение валидации класса Fields.
    """

    def validate(self):
        """
        Валидация полученных в параметрах значений.
        """
        fields = self._calculate_dynamic_fields(**self.all)

        MandatoryFields(**fields)
        CustomExtensionFields(**fields)


class BaseEvent(Event):
    """
    Базовый логгер-класс с дефолтными параметрами
    """

    SYSLOG_HEADER = True  # добавляем дату, время, хост в начало лог-сообщения

    # базовые атрибуты лог-сообщения
    Version = 0
    DeviceProduct = 'YOUR_COMPANY'
    DeviceVersion = '0.8'
    DeviceVendor = 'IBS'
    DeviceEventClassID = 'base'
    Name = 'view name'
    Severity = 1

    def __init__(self):
        try:
            self.fields = CustomFields(
                syslog_flag=self.SYSLOG_HEADER,
                **self.__fields__,
            )
            self.fields.validate()
        except Exception as error:
            self.error_log(error)

    def __call__(self, **fields):
        """
        Добавление CustomFields для валидации данных и параметра «end» в конце лог-сообщения
        """
        try:
            if fields:
                fields = CustomFields(syslog_flag=self.SYSLOG_HEADER, **{**self.fields.all, **fields})
                fields.validate()
                fields.custom['end'] = int(time.time())
                self.emit(fields.render())
            else:
                self.fields.custom['end'] = int(time.time())
                self.emit(self.fields.render())
        except Exception as error:
            self.error_log(error)

    def error_log(self, error):
        """
        Отправка информационного лог-сообщения в случае ошибок
        при инициализации и вызове экземпляра текущего класса
        """
        fields = CustomFields(
            syslog_flag=self.SYSLOG_HEADER,
            **{
                **BaseEvent.__fields__,
                'msg': f'Ошибка при формировании лог-атрибутов: {error}',
            },
        )
        self.emit(fields.render())

    def send_log(self, msg, data):
        """
        Вызов __call__ для отправки лог-сообщения.
        """
        if not data:
            return self.__call__(msg=msg)
        return self.__call__(msg=msg, **data)

    def debug(self, msg=None, data=None):
        """
        Отправка лог-сообщения на уровне debug.
        """
        if LogLevels.is_debug():
            return self.send_log(msg, data)

    def info(self, msg=None, data=None):
        """
        Отправка лог-сообщения на уровне info.
        """
        if LogLevels.is_info():
            return self.send_log(msg, data)

    def warning(self, msg=None, data=None):
        """
        Отправка лог-сообщения на уровне warning.
        """
        if LogLevels.is_warning():
            return self.send_log(msg, data)

    def error(self, msg=None, data=None):
        """
        Отправка лог-сообщения на уровне error.
        """
        if LogLevels.is_error():
            return self.send_log(msg, data)

    def critical(self, msg=None, data=None):
        """
        Отправка лог-сообщения на уровне critical.
        """
        if LogLevels.is_critical():
            return self.send_log(msg, data)