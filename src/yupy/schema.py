from dataclasses import field, dataclass
from typing import Any, List, Optional, Generic, TypeVar, Self, Type

from yupy.ischema import ISchema, TransformFunc, ValidatorFunc
from yupy.locale import locale
from yupy.validation_error import ErrorMessage, ValidationError, Constraint

__all__ = ('Schema',)

_T = TypeVar('_T')


@dataclass
class Schema(Generic[_T], ISchema[_T]):  # Implement ISchema
    _type: Type[_T] = field(default=Any)
    _transforms: List[TransformFunc] = field(init=False, default_factory=list)
    _validators: List[ValidatorFunc] = field(init=False, default_factory=list)
    _optional: bool = True
    _required: Optional[ErrorMessage] = locale["required"]
    _nullability: bool = False
    _not_nullable: ErrorMessage = locale["not_nullable"]

    @property
    def optional(self) -> bool:
        return self._optional

    def required(self, message: ErrorMessage = locale["required"]) -> Self:
        self._required: Optional[ErrorMessage] = message
        self._optional: bool = False
        return self

    def not_required(self) -> Self:
        self._optional: bool = True
        return self

    def nullable(self) -> Self:
        self._nullability: bool = True
        return self

    def not_nullable(self, message: ErrorMessage = locale["not_nullable"]) -> Self:
        self._nullability: bool = False
        self._not_nullable: ErrorMessage = message
        return self

    def _nullable_check(self) -> None:
        if not self._nullability:
            raise ValidationError(
                Constraint("nullable", None, self._not_nullable),
            )

    def _type_check(self, value: Any) -> None:
        type_: type[_T] = self._type
        if type_ is Any:
            return
        if not isinstance(value, type_):
            raise ValidationError(
                Constraint("type", (type_, type(value)), locale["type"])
            )

    def transform(self, func: TransformFunc) -> Self:
        self._transforms: List[TransformFunc]
        self._transforms.append(func)
        return self

    def test(self, func: ValidatorFunc) -> Self:
        self._validators: List[ValidatorFunc]
        self._validators.append(func)
        return self

    def validate(self, value: _T, abort_early: bool = True, path: str = "") -> _T:
        try:
            if value is None:
                self._nullable_check()
                return None

            self._type_check(value)

            transformed: _T = value
            for t in self._transforms:
                transformed = t(transformed)

            for v in self._validators:
                v(transformed)
            return transformed
        except ValidationError as err:
            raise ValidationError(err.constraint, path)
