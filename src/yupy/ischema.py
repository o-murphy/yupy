from types import UnionType
from typing import Protocol, TypeVar, Callable, Any, TypeAlias

from yupy.validation_error import ErrorMessage

_T = TypeVar('_T')
_SchemaExpectedType: TypeAlias = type | UnionType | tuple[Any, ...]
# _SchemaExpectedType = TypeVar('_SchemaExpectedType', type, UnionType, tuple[Any, ...])


TransformFunc = Callable[[Any], Any]
ValidatorFunc = Callable[[_T], _T]


class ISchema(Protocol[_T]):
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

    def test(self, func: ValidatorFunc) -> 'ISchema': ...

    def validate(self, value: _T, abort_early: bool = True, path: str = "") -> _T: ...
