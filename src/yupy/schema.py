from dataclasses import field, dataclass
from typing import Any, List, TypeVar, Generic

from yupy.ischema import TransformFunc, ValidatorFunc, _SchemaExpectedType
from yupy.locale import locale
from yupy.validation_error import ErrorMessage, ValidationError, Constraint

__all__ = ('Schema',)

_S = TypeVar('_S')


@dataclass
class Schema(Generic[_S]):  # Implement ISchema
    _type: _SchemaExpectedType = field(default=object)
    _transforms: List[TransformFunc] = field(init=False, default_factory=list)
    _validators: List[ValidatorFunc] = field(init=False, default_factory=list)
    _optional: bool = True
    _required: ErrorMessage = locale["required"]
    _nullability: bool = False
    _not_nullable: ErrorMessage = locale["not_nullable"]

    _Self = TypeVar('_Self', bound='Schema')

    @property
    def optional(self) -> bool:
        return self._optional

    def required(self: _Self, message: ErrorMessage = locale["required"]) -> _Self:
        self._required: ErrorMessage = message
        self._optional: bool = False
        return self

    def not_required(self: _Self) -> _Self:
        self._optional: bool = True
        return self

    def nullable(self: _Self) -> _Self:
        self._nullability: bool = True
        return self

    def not_nullable(self: _Self, message: ErrorMessage = locale["not_nullable"]) -> _Self:
        self._nullability: bool = False
        self._not_nullable: ErrorMessage = message
        return self

    def _nullable_check(self: _Self, value: Any) -> None:
        if not self._nullability:
            raise ValidationError(
                Constraint("nullable", self._not_nullable),
                invalid_value=value
            )

    def _type_check(self: _Self, value: Any) -> None:
        type_ = self._type
        if type_ is Any:
            return
        if not isinstance(value, type_):
            raise ValidationError(
                Constraint("type", locale["type"], type_, type(value)),
                invalid_value=value
            )

    def transform(self: _Self, func: TransformFunc) -> _Self:
        self._transforms: List[TransformFunc]
        self._transforms.append(func)
        return self

    def test(self: _Self, func: ValidatorFunc) -> _Self:
        self._validators.append(func)
        return self

    def _transform(self: _Self, value: Any) -> Any:
        transformed: Any = value
        for t in self._transforms:
            transformed = t(transformed)
        return transformed

    def validate(self: _Self, value: Any, abort_early: bool = True, path: str = "") -> Any:
        try:
            if value is None:
                self._nullable_check(value)
                return value

            self._type_check(value)

            transformed = self._transform(value)

            for v in self._validators:
                v(transformed)
            return transformed
        except ValidationError as err:
            raise ValidationError(err.constraint, path, invalid_value=value)
