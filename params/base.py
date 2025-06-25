"""
Классы с базовыми лог-параметрами - они применяются, когда ViewSet наследует CEFLogMixin.
"""

from ..utils import RESTMethods
from .main import BaseParams, error_handler, msg_modification


class GetBaseParams(BaseParams):
    """
    Базовые параметры GET-запросов
    """

    def set_cef_params(self):
        return {
            self.DeviceEventClassID.__name__: self.DeviceEventClassID(),
            self.Severity.__name__: self.Severity(),
            self.msg.__name__: self.msg(),
        }

    @error_handler
    def apply_condition(self):
        return self.instance.request.method == RESTMethods.GET

    def DeviceEventClassID(self):  # noqa: N802
        return RESTMethods.DeviceEventClassID.GET

    def Severity(self):  # noqa: N802
        return RESTMethods.Severity.GET

    def msg(self):
        return RESTMethods.Message.GET


class GetRetrieveParams(GetBaseParams):
    """
    Базовые параметры GET-retrieve-запроса
    """

    @error_handler
    def apply_condition(self):
        return (
            super().apply_condition()
            and getattr(self.instance, 'action', None) == 'retrieve'
            and hasattr(self.instance, 'names_for_logger')
        )

    @error_handler
    @msg_modification
    def msg(self):
        return f'Просматривает {self.instance.names_for_logger[1]}'


class GetListParams(GetBaseParams):
    """
    Базовые параметры GET-list-запроса
    """

    @error_handler
    def apply_condition(self):
        return (
            super().apply_condition()
            and getattr(self.instance, 'action', None) == 'list'
            and hasattr(self.instance, 'names_for_logger')
        )

    @error_handler
    def msg(self):
        return f'Просматривает список {self.instance.names_for_logger[2]} в системе'


class PostBaseParams(BaseParams):
    """
    Базовые парпаметры POST-запроса
    """

    def set_cef_params(self):
        return {
            self.DeviceEventClassID.__name__: self.DeviceEventClassID(),
            self.Severity.__name__: self.Severity(),
            self.msg.__name__: self.msg(),
        }

    @error_handler
    def apply_condition(self):
        return self.instance.request.method == RESTMethods.POST

    def DeviceEventClassID(self):  # noqa: N802
        return RESTMethods.DeviceEventClassID.POST

    def Severity(self):  # noqa: N802
        return RESTMethods.Severity.POST

    @error_handler
    def msg(self):
        return f'Создает {self.instance.names_for_logger[0]}'


class DeleteBaseParams(BaseParams):
    """
    Базовые параметры DELETE-запроса
    """

    def set_cef_params(self):
        return {
            self.DeviceEventClassID.__name__: self.DeviceEventClassID(),
            self.Severity.__name__: self.Severity(),
            self.msg.__name__: self.msg(),
        }

    @error_handler
    def apply_condition(self):
        return self.instance.request.method == RESTMethods.DELETE

    def DeviceEventClassID(self):  # noqa: N802
        return RESTMethods.DeviceEventClassID.DELETE

    def Severity(self):  # noqa: N802
        return RESTMethods.Severity.DELETE

    @error_handler
    @msg_modification
    def msg(self):
        return f'Удаляет {self.instance.names_for_logger[0]}'


class PatchBaseParams(BaseParams):
    """
    Базовые параметры PATCH-запроса
    """

    def set_cef_params(self):
        return {
            self.DeviceEventClassID.__name__: self.DeviceEventClassID(),
            self.Severity.__name__: self.Severity(),
            self.msg.__name__: self.msg(),
        }

    @error_handler
    def apply_condition(self):
        return self.instance.request.method == RESTMethods.PATCH

    def DeviceEventClassID(self):  # noqa: N802
        return RESTMethods.DeviceEventClassID.PATCH

    def Severity(self):  # noqa: N802
        return RESTMethods.Severity.PATCH

    @error_handler
    @msg_modification
    def msg(self):
        return f'Обновляет {self.instance.names_for_logger[1]}'
