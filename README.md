# CEF LOGGERS

Модуль с интерфейсами для логирования событий. 

### Преимущества использования модуля
* Возможность переопределения существующих и создания собственных классов с лог-параметрами под любой случай 
* Возможность наследования класса-миксина в любой ViewSet для вывода дефолтных лог-сообщений
* Возможность гибкого формирования и вывода лог-сообщения в любом месте кода
* Высокая отказоустойчивость при возбуждении исключений


## Структура модуля

```mermaid
cef_loggers
    params
    events
    mixins
    utils
```

* [events](./events.py) – классы событий для валидации параметров и вывода лог-собщений
* [mixins](./mixins.py) – классы-миксины для наследования во ViewSet
* [params](./params.py) – классы с лог-параметрами
* [utils](./utils.py) – вспомогательные классы и методы


## Использование модуля 

### 1. Наследование CEFLogMixin
Для вывода дефолтного лог-сообщения CEF-формата досаточно наследовать CEFLogMixin из [mixins](./mixins.py) во ViewSet.
Этот класс-миксин может выводить как базовый, так и расширенный лог. Схема публикации лог-сообщений с помощью 
CEFLogMixin описана в [схеме на странице confluence](https://conf.ibs.ru/x/3MQvEg). Для начала разберем, как выводится
базовый лог:
```
from cef_loggers import CEFLogMixin


class ProjectEventViewSet(
    ...
    CEFLogMixin,
    viewsets.ModelViewSet,
): 
    ...
    names_for_logger = ('событие', 'событие', 'событий')
    ...
```
По умолчанию переменная `names_for_logger` = `('объект', 'объект', 'объектов')`. Она отвечает за модификацию параметра 
`msg` в лог-сообщении в зависимости от метода запроса и `action`. Таким образом, `msg` может быть равен: 
* Если `GET-запрос` и `action=retrieve`, то `msg = просматривает {names_for_logger[1]} {идентификатор}`
* Если `GET-запрос` и `action=list`, то `msg = просматривает список {names_for_logger[2]} в системе`
* Если `PATCH-запрос`, то `msg = обновляет {names_for_logger[1]} {идентификатор}`
* Если `DELETE-запрос`, то `msg = удаляет {names_for_logger[0]} {идентификатор}`
* Если `POST-запрос`, то `msg = создает {names_for_logger[0]}`

В примере с `ProjectEventViewSet` могут быть выведены следующие лог-сообщения: 
#### При GET-запросе (`action=retrieve`): 

`2024-02-12T10:20:19.567372+00:00 CEF:0|IBS|YOUR_COMPANY|0.8|view|project-events|3|externalId=1
shost=your_host src=192.168.65.1 suser=Куратов Проектович 
dhost=your_host/api/projects/7a9a10ca-7664-4e47-8ee7-5445d54c0ff4/events/ef65cd6e-df40-4d3a-a65f-01f54e00cb44/ 
msg=Просматривает событие ef65cd6e-df40-4d3a-a65f-01f54e00cb44 outcome=success end=1707733219`

#### При POST-запросе: 

`2024-02-12T10:24:20.964072+00:00 CEF:0|IBS|YOUR_COMPANY|0.8|create|project-events|6|externalId=2 
shost=your_host src=192.168.65.1 suser=Куратов Проектович 
dhost=your_host/api/projects/7a9a10ca-7664-4e47-8ee7-5445d54c0ff4/events/ msg=Создает событие outcome=success 
end=1707733460`

#### При PATCH-запросе: 

`2024-02-12T10:25:22.741676+00:00 CEF:0|IBS|YOUR_COMPANY|0.8|update|project-events|6|externalId=3 shost=your_host 
src=192.168.65.1 suser=Куратов Проектович 
dhost=your_host/api/projects/7a9a10ca-7664-4e47-8ee7-5445d54c0ff4/events/c07fc630-0af2-49cb-ae43-a826ba545278/ 
msg=Обновляет событие c07fc630-0af2-49cb-ae43-a826ba545278 outcome=success end=1707733522`

#### При DELETE-запросе: 

`2024-02-12T10:46:25.403774+00:00 CEF:0|IBS|YOUR_COMPANY|0.8|delete|project-events|8|externalId=4 shost=your_host 
src=192.168.65.1 suser=Куратов Проектович 
dhost=your_host/api/projects/7a9a10ca-7664-4e47-8ee7-5445d54c0ff4/events/c07fc630-0af2-49cb-ae43-a826ba545278/ 
msg=Удаляет событие c07fc630-0af2-49cb-ae43-a826ba545278 outcome=success end=1707734785`

Для вывода лог-сообщения с расширенными параметрами (`cs1`, `cs2`  и др.) достаточно во `ViewSet` указать 
`cef_log = True`. Расширенный лог выводится только в случае, когда метод запроса равен `POST`, `PATCH` или `DELETE`:
```
from cef_loggers import CEFLogMixin


class ProjectEventViewSet(
    ...
    CEFLogMixin,
    viewsets.ModelViewSet,
): 
    ...
    cef_log = True
    ...
```
Теперь в `ProjectEventViewSet` будут выводиться расширенные лог-сообщения:

#### При POST-запросе: 

`2024-02-12T11:57:56.812776+00:00 CEF:0|IBS|YOUR_COMPANY|0.8|create|project-events|6|externalId=5 shost=your_host 
src=192.168.65.1 suser=Куратов Проектович 
dhost=your_host/api/projects/7a9a10ca-7664-4e47-8ee7-5445d54c0ff4/events/ msg=Создан объект 
cs1Label=Наименование объекта cs1=Объект модели «События» outcome=success end=1707739076`

#### При DELETE-запросе: 

`2024-02-12T13:29:58.936508+00:00 CEF:0|IBS|YOUR_COMPANY|0.8|delete|project-events|8|externalId=6 shost=your_host 
src=192.168.65.1 suser=Куратов Проектович 
dhost=your_host/api/projects/7a9a10ca-7664-4e47-8ee7-5445d54c0ff4/events/92af1a64-4616-49ee-bfdb-dba76b86ed2b/ 
msg=Удален объект cs1Label=Наименование объекта cs1=Объект модели «События» 
outcome=success end=1707744598`

#### При PATCH-запросе: 

`2024-02-12T13:29:58.936508+00:00 CEF:0|IBS|YOUR_COMPANY|0.8|update|project-events|6|externalId=7 shost=your_host 
src=192.168.65.1 suser=Куратов Проектович 
dhost=your_host/api/projects/7a9a10ca-7664-4e47-8ee7-5445d54c0ff4/events/92af1a64-4616-49ee-bfdb-dba76b86ed2b/ 
msg=Удален объект cs1Label=Наименование атриубута cs1=name cs2Label=Старое значение cs2=test cs3Label=Новое значение
cs3=test1 outcome=success end=1707744598`

#### При PATCH-запросе и наличии переменной is_extend_patch: 

`2024-02-12T13:29:58.936508+00:00 CEF:0|IBS|YOUR_COMPANY|0.8|update|project-events|6|externalId=8 shost=your_host 
src=192.168.65.1 suser=Куратов Проектович 
dhost=your_host/api/projects/7a9a10ca-7664-4e47-8ee7-5445d54c0ff4/events/92af1a64-4616-49ee-bfdb-dba76b86ed2b/ 
msg=Удален объект cs1Label=Наименование объекта cs1=EventModel object (92af1a64-4616-49ee-bfdb-dba76b86ed2b) 
cs2Label=Наименование атриубута cs2=name cs3Label=Старое значение cs3=test cs4Label=Новое значение cs4=test1
outcome=success end=1707744598`

### 2. Создание собственных классов с параметрами
Модуль предоставляет классы с параметрами для вывода дефолтных лог-сообщений. Все они наследуются от базового класса 
`Params`, в котором определены методы для установки каждого cef-параметра. Класс Params, как и все его наследники,
принимает обязательный аргумент `instance` - это экземпляр текущего ViewSet.

Если во ViewSet не указан флаг `cef_log`, то поиск параметров для лог-сообщения произойдет в классах:
* GetBaseParams
* GetListParams
* GetRetrieveParams
* PostBaseParams
* PatchBaseParams
* DeleteBaseParams

Если во ViewSet указан флаг `cef_log = True`, то поиск параметров произойдет в классах:
* PostCEFParams
* PatchCEFParams
* PatchCEFExtendParams
* DeleteCEFParams
* пользовательские классы при их наличии

> Набор классов, который используется при `cef_log = True` будет только в том случае, когда метода запроса равен
> равен `POST`, `PATCH`, `DELETE`.

У каждого класса с параметрами есть метод `apply_condition`, в котором прописано условие для использования 
cef-параметров этого класса, например: 
```
class PatchBaseParams(BaseParams):

    @error_handler
    def apply_condition(self):
        return self.instance.request.method == RESTMethods.PATCH
```
Таким образом, параметры класса `PatchBaseParams` будут применены, если метод запроса = `PATCH`. 

> Под капотом будет проверен метод `apply_condition` у каждого класса (набор классов зависит от флага `cef_log`). 
> В итоге будут использоваться параметры класса, у которого `apply_condition` вернул `True`. Если метод вернет 
> `True` в нескольких классах, то будет использован последний из них. 

#### Процесс создания собственного класса с параметрами:
Для того, чтобы задать собственные лог-параметры, нужно наследовать любой из классов с параметрами данного модуля и
переопределить его методы под свои нужны. 
1. Наследуемся от класса из библиотеки и переопределяем любые параметры
```python
from cef_loggers.params.cef import PatchCEFParams
from cef_loggers.params.main import error_handler

class CustomParams(PatchCEFParams):
    
    def cs1Label(self):
        return 'ЛЮБОЕ ЗНАЧЕНИЕ'
    
    @error_handler
    def cs1(self):
        return 'ЛЮБОЕ ЗНАЧЕНИЕ'
```
Здесь мы переопределили параметры `cs1` и `cs1Label` под свои нужды.
> Декоратор `@error_handler` используется для того, чтобы заоплнить параметр значением `None`, если при его вычислении 
> будет вызвано исключение. Рекомендуется использовать этот декоратор, если при вычислении параметра может возникнуть
> ошибка.

Можно переопределить метод `apply_condition`, если это требуется. В противном случае будет использован 
`apply_condition` базового класса.
```python
from cef_loggers.params import PatchCEFParams
from cef_loggers.params import error_handler

class CustomParams(PatchCEFParams):
    
    def cs1Label(self):
        return 'ЛЮБОЕ ЗНАЧЕНИЕ'
    
    @error_handler
    def cs1(self):
        return 'ЛЮБОЕ ЗНАЧЕНИЕ'

    def apply_condition(self):
        return 'signer' in self.instance.request.data
```

2. Во ViewSet добавляем метод `add_log_params`, который вернет список ваших пользовательских классов с параметрами:
```python
class ProjectEventViewSet(
    CEFLogMixin,
    viewsets.ModelViewSet,
):

    def add_log_params(self):
        return CustomParams(self), ...
```
> По задумке метод `add_log_params` должен возвращать итерируемый объект, но это необязательно. Можно указать лишь один
> класс, и это сработает корректно.

#### Готово! Теперь в лог-сообщении будут заданные вам параметры.

3. Изменение порядка и добавление новых параметров. В примере выше порядок и набор параметров будет таким же, как и в 
унаследованном классе. Если требуется это изменить, то можно переопределить метод `set_cef_params` - в нем можно 
переопределить порядок параметров `msg` и тех, что начинаются на `cs`, а также добавить новые параметры. При этом, 
обязательные параметры `src`, `dhost`, `shost`, `external_Id`, `ouctome` и др. будут добавлены в лог-сообщение 
автоматически в нужном порядке. Пример изменения порядка вывода и добавления новых параметров:
```python
from cef_loggers.params import PatchCEFParams

class CustomParams(PatchCEFParams):
    
    def set_cef_params(self):
        return {
            **super().set_cef_params(),
            'новый параметр': 'значение',
            'параметр': self.параметр(),
            'cs3Label': self.cs3Label(),
            'cs1Label': self.cs1Label(),
            'cs1': self.cs1(),
            'cs2Label': self.cs2Label(),
            'cs3': self.cs3(),
            'msg': self.msg(),
        }
    
    def параметр(self):
        return 'значение'
```
Теперь, будут выведены новые параметры - `новый параметр` и `парамет`. Параметр `cs3Label` будет выведен сразу после
новых параметров, а за ним `cs1Label`, `cs1`, `cs2Label`, `cs3` и `msg`.
> Переопределять порядок параметров следует осторожно, предварительно взглянув на реализацию метода `set_cef_params` в 
> наследуемом классе. В базовом классе этот метод определяет параметры `DeviceEventClassID`, `Severity` и `msg`, а
> дочерние классы переопределяют метод, дополняя его параметрами `cs1`, `cs2` и так далее.
### 3. Отправка лог-сообщения в любом месте кода
Для отправки лог-сообщения в любом месте кода можно использовать `logger`.
```python
from cef_loggers import logger
from cef_loggers.utils import get_required_log_attributes


def list(self, request, *args, **kwargs):
    ...
    #  формируем словарь атрибутов из request при необходимотсти
    attributes = get_required_log_attributes(request)
    #  добавляем любые атрибуты по желанию
    attributes.update({'атрибут': 'значение', ...})
    #  отправляем лог-сообщение на нужном уровне (debug, info или др.)
    logger.info('Сообщение лога', attributes)
```