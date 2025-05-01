from typing import Protocol, TypeVar, Callable, Any, Optional, Type

from yupy.validation_error import ErrorMessage

_T = TypeVar('_T')

TransformFunc = Callable[[Any], Any]
ValidatorFunc = Callable[[_T], _T]


class ISchema(Protocol[_T]):
    _type: Type[_T]
    _transforms: list[TransformFunc]
    _validators: list[ValidatorFunc]
    _optional: bool
    _required: Optional[ErrorMessage]
    _nullability: bool
    _not_nullable: ErrorMessage

    @property
    def optional(self) -> bool: ...

    def required(self, message: ErrorMessage) -> 'Self': ...

    def not_required(self) -> 'Self': ...

    def nullable(self) -> 'Self': ...

    def not_nullable(self, message: ErrorMessage) -> 'Self': ...

    def transform(self, func: TransformFunc) -> 'Self': ...

    def test(self, func: ValidatorFunc) -> 'Self': ...

    def validate(self, value: _T, abort_early: bool = True, path: str = "") -> _T: ...
