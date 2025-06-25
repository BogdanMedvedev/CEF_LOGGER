"""
Классы с CEF (расширенными) параметрами - они применяются, когда во ViewSet
установлен флаг cef_log = True.
"""

from ..utils import LogLabels, RESTMethods
from .main import CEFBaseParams, CEFBasePatchParams, CEFExtendPatchParams, error_handler


class PostCEFParams(CEFBaseParams):
    """
    CEF-параметры для POST-запроса
    """

    def set_cef_params(self):
        return {
            self.DeviceEventClassID.__name__: self.DeviceEventClassID(),
            self.Severity.__name__: self.Severity(),
            self.msg.__name__: self.msg(),
            self.cs1Label.__name__: self.cs1Label(),
            self.cs1.__name__: self.cs1(),
        }

    @error_handler
    def apply_condition(self):
        return self.instance.request.method == RESTMethods.POST

    def DeviceEventClassID(self):  # noqa: N802
        return RESTMethods.DeviceEventClassID.POST

    def Severity(self):  # noqa: N802
        return RESTMethods.Severity.POST

    def msg(self):
        return RESTMethods.Message.POST

    def cs1Label(self):  # noqa: N802
        return LogLabels.object_name

    @error_handler
    def cs1(self):
        if not self.instance.error:
            if getattr(self.instance.queryset.model._meta, 'get_latest_by', None):
                return self.instance.queryset.latest()
        return f'Объект модели «{self.instance.queryset.model._meta.verbose_name}»'


class DeleteCEFParams(CEFBaseParams):
    """
    CEF-параметры для DELETE-запроса
    """

    def set_cef_params(self):
        return {
            self.DeviceEventClassID.__name__: self.DeviceEventClassID(),
            self.Severity.__name__: self.Severity(),
            self.msg.__name__: self.msg(),
            self.cs1Label.__name__: self.cs1Label(),
            self.cs1.__name__: self.cs1(),
        }

    @error_handler
    def apply_condition(self):
        return self.instance.request.method == RESTMethods.DELETE

    def DeviceEventClassID(self):  # noqa: N802
        return RESTMethods.DeviceEventClassID.DELETE

    def Severity(self):  # noqa: N802
        return RESTMethods.Severity.DELETE

    def msg(self):
        return RESTMethods.Message.DELETE

    def cs1Label(self):  # noqa: N802
        return LogLabels.object_name

    @error_handler
    def cs1(self):
        if not self.instance.error:
            return self.instance.old_object
        return f'Объект модели «{self.instance.queryset.model._meta.verbose_name}»'


class PatchCEFParams(CEFBasePatchParams):
    """
    CEF-параметры для PATCH-запроса
    """

    @error_handler
    def apply_condition(self):
        return self.instance.request.method == RESTMethods.PATCH

    def DeviceEventClassID(self):  # noqa: N802
        return RESTMethods.DeviceEventClassID.PATCH

    def Severity(self):  # noqa: N802
        return RESTMethods.Severity.PATCH

    def cs1Label(self):  # noqa: N802
        return LogLabels.attribute_name

    def cs2Label(self):  # noqa: N802
        return LogLabels.old_value

    def cs3Label(self):  # noqa: N802
        return LogLabels.new_value

    @error_handler
    def cs1(self):
        return getattr(self, 'changed_key', str(None))

    @error_handler
    def cs2(self):
        return self.instance.old_object.get(self.cs1()) or str(None)

    @error_handler
    def cs3(self):
        return self.instance.new_object.get(self.cs1()) or str(None)

    def msg(self):
        return RESTMethods.Message.PATCH

    def set_cef_params(self):
        return {
            self.DeviceEventClassID.__name__: self.DeviceEventClassID(),
            self.Severity.__name__: self.Severity(),
            self.msg.__name__: self.msg(),
            self.cs1Label.__name__: self.cs1Label(),
            self.cs1.__name__: self.cs1(),
            self.cs2Label.__name__: self.cs2Label(),
            self.cs2.__name__: self.cs2(),
            self.cs3Label.__name__: self.cs3Label(),
            self.cs3.__name__: self.cs3(),
        }


class PatchCEFExtendParams(CEFExtendPatchParams):
    """
    CEF-параметры для расширенного PATCH-запроса
    """

    @error_handler
    def apply_condition(self):
        return self.instance.request.method == RESTMethods.PATCH and getattr(
            self.instance, 'is_extend_patch', None
        )

    def DeviceEventClassID(self):  # noqa: N802
        return RESTMethods.DeviceEventClassID.PATCH

    def Severity(self):  # noqa: N802
        return RESTMethods.Severity.PATCH

    def cs1Label(self):  # noqa: N802
        return LogLabels.object_name

    def cs2Label(self):  # noqa: N802
        return LogLabels.attribute_name

    def cs3Label(self):  # noqa: N802
        return LogLabels.old_value

    def cs4Label(self):  # noqa: N802
        return LogLabels.new_value

    def msg(self):
        return RESTMethods.Message.PATCH

    @error_handler
    def cs1(self):
        return self.instance.get_log_instance()

    @error_handler
    def cs2(self):
        return getattr(self, 'changed_key', str(None))

    @error_handler
    def cs3(self):
        return self.instance.old_object.get(self.cs2()) or str(None)

    @error_handler
    def cs4(self):
        return self.instance.new_object.get(self.cs2()) or str(None)

    def set_cef_params(self):
        return {
            self.DeviceEventClassID.__name__: self.DeviceEventClassID(),
            self.Severity.__name__: self.Severity(),
            self.msg.__name__: self.msg(),
            self.cs1Label.__name__: self.cs1Label(),
            self.cs1.__name__: self.cs1(),
            self.cs2Label.__name__: self.cs2Label(),
            self.cs2.__name__: self.cs2(),
            self.cs3Label.__name__: self.cs3Label(),
            self.cs3.__name__: self.cs3(),
            self.cs4Label.__name__: self.cs4Label(),
            self.cs4.__name__: self.cs4(),
        }
