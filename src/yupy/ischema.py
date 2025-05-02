from types import UnionType
from typing import Protocol, TypeVar, Callable, Any, TypeAlias, runtime_checkable

from yupy.validation_error import ErrorMessage

_P = TypeVar('_P', covariant=True)
_SchemaExpectedType: TypeAlias = type | UnionType | tuple[Any, ...]

TransformFunc: TypeAlias = Callable[[Any], Any]
ValidatorFunc: TypeAlias = Callable[[_P], _P]


@runtime_checkable
class ISchema(Protocol[_P]):
    _type: _SchemaExpectedType
    _transforms: list[TransformFunc]
    _validators: list[ValidatorFunc]
    _optional: bool
    _required: ErrorMessage
    _nullability: bool
    _not_nullable: ErrorMessage

    @property
    def optional(self) -> bool: ...

    def required(self, message: ErrorMessage) -> 'ISchema': ...

    def not_required(self) -> 'ISchema': ...

    def nullable(self) -> 'ISchema': ...

    def not_nullable(self, message: ErrorMessage) -> 'ISchema': ...

    def transform(self, func: TransformFunc) -> 'ISchema': ...

    def _transform(self, value: Any) -> Any: ...

    def test(self, func: ValidatorFunc) -> 'ISchema': ...

    def validate(self, value: Any, abort_early: bool = True, path: str = "") -> Any: ...

    def _nullable_check(self, value: Any) -> None: ...

    def _type_check(self, value: Any) -> None: ...
