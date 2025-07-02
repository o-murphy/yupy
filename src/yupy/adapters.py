from copy import deepcopy
from typing import Any, TypeVar, Protocol, runtime_checkable, Union

from typing_extensions import Self

from yupy.ischema import ISchema, ErrorMessage
from yupy.locale import locale
from yupy.validation_error import ValidationError, Constraint, _EMPTY_MESSAGE_

_REQUIRED_UNDEFINED_ = TypeVar("_REQUIRED_UNDEFINED_")

__all__ = (
    'ISchemaAdapter',
    'SchemaAdapter',
    'SchemaDefaultAdapter',
    'SchemaRequiredAdapter',
    'SchemaImmutableAdapter',
    '_REQUIRED_UNDEFINED_',
)


@runtime_checkable
class ISchemaAdapter(Protocol):
    _schema: Union[ISchema, 'ISchemaAdapter']
    _message: ErrorMessage

    # def __init__(self, schema: Union[ISchema, 'ISchemaAdapter'],
    #              message: ErrorMessage = _EMPTY_MESSAGE_) -> None: ...

    @property
    def schema(self) -> Union[ISchema, 'ISchemaAdapter']: ...

    def validate(self, value: Any = None, abort_early: bool = True, path: str = "~") -> Any: ...


class SchemaAdapter:
    _schema: Union[ISchema, ISchemaAdapter]
    _message: ErrorMessage

    def __init__(self, schema: Union[ISchema, ISchemaAdapter],
                 message: ErrorMessage = _EMPTY_MESSAGE_) -> None:
        self._schema = schema
        self._message = message

    @property
    def schema(self) -> Union[ISchema, ISchemaAdapter]:
        return self._schema

    def validate(self, value: Any = None, abort_early: bool = True, path: str = "~") -> Any:
        return self._schema.validate(value, abort_early, path)


class SchemaDefaultAdapter(SchemaAdapter):
    _default: Any
    _ensure: bool

    def __init__(self,
                 default_value: Any,
                 schema: Union[ISchema, ISchemaAdapter],
                 message: ErrorMessage = _EMPTY_MESSAGE_):
        super().__init__(schema, message)
        self._default = default_value
        self._ensure = False

    def ensure(self) -> Self:
        self._ensure = True
        return self

    def validate(self, value: Any = None, abort_early: bool = True, path: str = "~") -> Any:
        if value is None:
            value = self._default
        try:
            return super().validate(value, abort_early, path)
        except ValidationError as e:
            if not self._ensure:
                raise e
        return self._default


class SchemaRequiredAdapter(SchemaAdapter):

    def __init__(self, schema: Union[ISchema, ISchemaAdapter],
                 message: ErrorMessage = locale['required']):
        super().__init__(schema, message)

    def validate(self, value: Any = _REQUIRED_UNDEFINED_, abort_early: bool = True, path: str = "~", path_=None) -> Any:
        if value is _REQUIRED_UNDEFINED_:
            raise ValidationError(
                Constraint("required", self._message, path),
                path, invalid_value=value
            )
        return self._schema.validate(value, abort_early, path)


class SchemaImmutableAdapter(SchemaAdapter):
    def __init__(self, schema: Union[ISchema, ISchemaAdapter],
                 message: ErrorMessage = _EMPTY_MESSAGE_):
        super().__init__(schema, message)

    def validate(self, value: Any = _REQUIRED_UNDEFINED_, abort_early: bool = True, path: str = "~", path_=None) -> Any:
        value_copy = deepcopy(value)
        self._schema.validate(value_copy, abort_early, path)
        return value
