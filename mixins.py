"""
Клас-миксин запускает процессы формирования параметров и отправки лог-сообщения
в родительском ViewSet
"""

from typing import Iterable, Union

from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from rest_framework.response import Response

from . import logger
from .params.base import (
    DeleteBaseParams,
    GetBaseParams,
    GetListParams,
    GetRetrieveParams,
    PatchBaseParams,
    PostBaseParams,
)
from .params.cef import DeleteCEFParams, PatchCEFExtendParams, PatchCEFParams, PostCEFParams
from .params.main import ParamsSelector, error_handler
from .utils import LogLevels, RESTMethods


class CEFLogMixin(RESTMethods):
    """
    Класс-миксин для формирования и отправки лог-сообщений.
    """

    # флаги, определяющие формат логов
    cef_log = disable_log = is_extend_patch = False

    # перечисление методов, для которых не нужен CEF-лог
    exclude_method_for_cef_log, exclude_action_for_cef_log = (), ()

    # возникшнее исключение
    error: Exception = None

    # экземпляр класса с лог-параметрами
    params: ParamsSelector

    # ответ на запрос
    response: Union[Exception, Response]

    # атрибуты для сравнения объектов
    old_object = new_object = {}
    changed_fields: tuple

    # наименования для базовых лог-сообщений, они переопределяется во ViewSet
    names_for_logger: tuple = ('объект', 'объект', 'объектов')

    def check_response(self, request, *args, **kwargs):
        """
        Метод для получения response.
        """
        try:
            self.response = super().dispatch(request, *args, **kwargs)
        except Exception as error:
            self.error = self.response = error

    def send_response(self):
        """
        Метод для отправки ответа на запрос.
        """
        self.send_log()
        if self.error:
            raise self.error
        return self.response

    def add_log_params(self):
        """
        Метод для добавления частных реализаций BaseParams во ViewSet.

        Returns:
            response (Iterable[BaseParams]): итерируемый объект с экземплярами BaseParams.
        """
        pass

    def _get_valid_params(self):
        """
        Метод для проверки и модификации данных из add_log_params.
        """
        private_params = self.add_log_params()
        if not private_params:
            return ()
        elif not isinstance(private_params, Iterable):
            return (private_params,)
        return private_params

    def set_base_params(self):
        """
        Формирование параметров базового лог-сообщения.
        """
        self.params = ParamsSelector(
            GetBaseParams(self),
            GetListParams(self),
            GetRetrieveParams(self),
            PostBaseParams(self),
            PatchBaseParams(self),
            DeleteBaseParams(self),
        )

    def set_cef_params(self):
        """
        Формирование параметров расширенного лог-сообщения.
        """
        self.params = ParamsSelector(
            PostCEFParams(self),
            PatchCEFParams(self),
            PatchCEFExtendParams(self),
            DeleteCEFParams(self),
            *self._get_valid_params(),
        )

    def send_log(self):
        """
        Метод для отправки лог-сообщения.
        """
        if changed_fields := getattr(self, 'changed_fields', None):
            for key in changed_fields:
                self.params.log_params.changed_key = key
                logger(**self.params.set_cef_params())
        else:
            logger(**self.params.set_cef_params())

    @error_handler
    def get_log_instance(self):
        """
        Метод для получения идентификатора объекта из kwargs. Переопределяется в каждом ViewSet.
        """
        return self.kwargs.get('sid')

    def dispatch(self, request, *args, **kwargs):
        """
        Переопределение базового dispatch для формирования лога перед отправкой ответа.

        Returns:
            Response (Response|Exception): объект ответа на запрос или возникшее исключение
        """
        if (
                self.disable_log
                or not LogLevels.is_cef_level()
                or request.method in self.exclude_method_for_cef_log
                or (hasattr(self, 'action') and self.action in self.exclude_action_for_cef_log)
        ):
            return super().dispatch(request, *args, **kwargs)

        if request.method == self.GET or not self.cef_log:
            self.check_response(request, *args, **kwargs)
            self.set_base_params()
            return self.send_response()
        if self.is_modifying_method(request.method):
            self.check_object_change(request, *args, **kwargs)
            if not hasattr(self, 'response'):
                self.check_response(request, *args, **kwargs)
        else:
            self.check_response(request, *args, **kwargs)
        self.set_cef_params()
        return self.send_response()

    @error_handler
    def check_object_change(self, request, *args, **kwargs):
        """
        Фиксация истории изменений в объектах связанного queryset.
        """
        self.old_object = self._get_comparative_object(request)
        self.check_response(request, *args, **kwargs)
        if request.method != self.DELETE and not self.error:
            self.new_object = self._get_comparative_object(request)
            self.changed_fields = tuple(
                key for key, value in self.new_object.items() if self.old_object.get(key) != value
            )

    def _get_comparative_object(self, request):
        """
        Получение объекта модели в виде словаря.

        Returns:
            comparative_object (dict)
        """
        comparative_object = {}
        if lookup_url_kwarg := getattr(self, 'lookup_url_kwarg', None) or getattr(
            self, 'lookup_field', None
        ):
            if pk := self.kwargs.get(lookup_url_kwarg):
                try:
                    if request.method == self.DELETE:
                        return self.queryset.get(pk=pk)
                    comparative_object = model_to_dict(self.queryset.get(pk=pk))
                except ObjectDoesNotExist as error:
                    logger.debug(f'Ошибка при получении объекта: {error}')
        return comparative_object
