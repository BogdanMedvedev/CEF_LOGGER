"""
Базовые классы и декораторы для формирования лог-параметров, на которых построен данный модуль.
"""

from abc import ABC, abstractmethod
from functools import wraps

from .. import logger
from ..utils import Outcomes, get_dhost, external_counter, visitor_ip_address, get_dst


def error_handler(func):
    """
    Декоратор для отправки информационного лог-сообщения в случае вызова исключения.
    """

    @wraps(func)
    def catch_error(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as error:
            logger.debug(f'Ошибка при вычислении {func.__name__}: {error}')

    return catch_error


def msg_modification(func):
    """
    Декоратор для добавления идентификатора объекта в msg.
    """

    @wraps(func)
    def check_log_instance(self, *args, **kwargs):
        """
        Проверяем наличие log_instance во ViewSet.
        """
        msg = func(self, *args, **kwargs)
        if log_instance := self.instance.get_log_instance():
            return f'{msg} {log_instance}'
        return msg

    return check_log_instance


def required_params(func):
    """
    Декоратор добавляет обязательные параметры в set_cef_params.
    """

    @wraps(func)
    def add_params(self, *args, **kwargs):
        """
        Формирование и добавление обязательных лог-параметров.
        """
        request_params = RequestParams(self.log_params.instance).set_cef_params()
        outcome_params = OutcomeParams(self.log_params.instance).set_cef_params()
        return {
            **request_params,
            **func(self, *args, **kwargs),
            **outcome_params,
        }

    return add_params


class BaseParamsMethods(ABC):
    """Базовый класс с методами для лог-параметрамов."""

    def __init__(self, instance):
        """
        instance - экземпляр ViewSet, дополненный атрибутами CEFLogMixin.
        """
        self.instance = instance

    @abstractmethod
    def set_cef_params(self):
        """
        Метод для установки лог-атрибутов в формате:
        {'cs1': value1, 'cs2': value2, ...}
        """
        pass

    @abstractmethod
    def apply_condition(self):
        """
        Метод для установки условий применения класса-параметров в формате:
        return self.request.method == 'GET' and ...
        """
        pass


class BaseRequestParams(BaseParamsMethods):
    """Базовый класс с параметрами, которые вычисляются из request."""

    @abstractmethod
    def Name(self):  # noqa: N802
        """
        Наименование события.
        """
        pass

    @abstractmethod
    def externalId(self):  # noqa: N802
        """
        Уникальный идентификатор события.
        """
        pass

    @abstractmethod
    def shost(self):
        """
        Адрес отправителя.
        """
        pass

    @abstractmethod
    def src(self):
        """
        IP-адрес.
        """
        pass

    @abstractmethod
    def suser(self):
        """
        Пользователь-инициатор события.
        """
        pass

    @abstractmethod
    def dhost(self):
        """
        Адрес назначения.
        """
        pass


class BaseParams(BaseParamsMethods):
    """Базовый класс с базовыми лог-параметрами"""

    @abstractmethod
    def DeviceEventClassID(self):  # noqa: N802
        """
        Краткое описание события.
        """
        pass

    @abstractmethod
    def Severity(self):  # noqa: N802
        """
        Уровень важности события.
        """
        pass

    @abstractmethod
    def msg(self):
        """
        Лог-сообщение.
        """
        pass


class CEFBaseParams(BaseParams):
    """Базовый класс с CEF-параметрами"""

    @abstractmethod
    def cs1Label(self):  # noqa: N802
        """
        Заголовок №1.
        """
        pass

    @abstractmethod
    def cs1(self):
        """
        Значение №1.
        """
        pass


class CEFBasePatchParams(BaseParams):
    """Базовый класс с CEF-параметрами для обновления сущностей"""

    @abstractmethod
    def cs2Label(self):  # noqa: N802
        """
        Заголовок №2.
        """
        pass

    @abstractmethod
    def cs3Label(self):  # noqa: N802
        """
        Заголовок №3.
        """
        pass

    @abstractmethod
    def cs2(self):
        """
        Значение №2.
        """
        pass

    @abstractmethod
    def cs3(self):
        """
        Значение №3.
        """
        pass


class CEFExtendPatchParams(CEFBasePatchParams):
    """Базовый класс с расширенными CEF-параметрами для обновления сущностей"""

    @abstractmethod
    def cs4Label(self):  # noqa: N802
        """
        Заголовок №4.
        """
        pass

    @abstractmethod
    def cs4(self):
        """
        Значение №4.
        """
        pass


class RequestParams(BaseRequestParams):
    """
    Параметры, вычисляемые на основе request.
    """

    def set_cef_params(self):
        return {
            self.Name.__name__: self.Name(),
            self.externalId.__name__: self.externalId(),
            self.shost.__name__: self.shost(),
            self.src.__name__: self.src(),
            self.suser.__name__: self.suser(),
            self.dhost.__name__: self.dhost(),
            self.dst.__name__: self.dst(),
        }

    def apply_condition(self):
        return True

    @error_handler
    def Name(self):  # noqa: N801, N802
        return self.instance.request.resolver_match.view_name

    @error_handler
    def externalId(self):  # noqa: N801, N802
        return external_counter()

    @error_handler
    def shost(self):
        return self.instance.request.get_host()

    @error_handler
    def src(self):
        return visitor_ip_address(self.instance.request)

    @error_handler
    def suser(self):
        return self.instance.request.user.profile.full_name

    @error_handler
    def dhost(self):
        return get_dhost(self.instance.request)

    @error_handler
    def dst(self):
        return get_dst()


class OutcomeParams(BaseParamsMethods):
    """
    Параметры, вычисляемые на основе response.
    """

    @error_handler
    def set_cef_params(self):
        return Outcomes.get_outcome(self.instance.response, self.instance.error)

    def apply_condition(self):
        return True


class ParamsSelector:
    """
    Класс для определения лог-параметров.
    """

    log_params: BaseParamsMethods

    def __init__(self, base_param: BaseParamsMethods, *params: BaseParamsMethods):
        """
        Все входящие параметры - экземпляры BaseParamsMethods.
        """
        try:
            for param in reversed(params):
                if param.apply_condition():
                    self.log_params = param
                    break
        except Exception as error:
            logger.debug(f'Ошибка в {ParamsSelector.__name__}: {error}')
        if not hasattr(self, 'log_params'):
            self.log_params = base_param

    @required_params
    def set_cef_params(self):
        return self.log_params.set_cef_params()
