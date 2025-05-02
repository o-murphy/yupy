from dataclasses import field, dataclass
from typing import Any, List, TypeVar, Generic

from yupy.ischema import ISchema, TransformFunc, ValidatorFunc, _SchemaExpectedType
from yupy.locale import locale
from yupy.validation_error import ErrorMessage, ValidationError, Constraint

__all__ = ('Schema',)

_T = TypeVar('_T')


@dataclass
class Schema(ISchema[_T], Generic[_T]):  # Implement ISchema
    _type: _SchemaExpectedType = field(default=object)
    _transforms: List[TransformFunc] = field(init=False, default_factory=list)
    _validators: List[ValidatorFunc] = field(init=False, default_factory=list)
    _optional: bool = True
    _required: ErrorMessage = locale["required"]
    _nullability: bool = False
    _not_nullable: ErrorMessage = locale["not_nullable"]

    @property
    def optional(self) -> bool:
        return self._optional

    def required(self, message: ErrorMessage = locale["required"]) -> 'Schema':
        self._required: ErrorMessage = message
        self._optional: bool = False
        return self

    def not_required(self) -> 'Schema':
        self._optional: bool = True
        return self

    def nullable(self) -> 'Schema':
        self._nullability: bool = True
        return self

    def not_nullable(self, message: ErrorMessage = locale["not_nullable"]) -> 'Schema':
        self._nullability: bool = False
        self._not_nullable: ErrorMessage = message
        return self

    def _nullable_check(self) -> None:
        if not self._nullability:
            raise ValidationError(
                Constraint("nullable", None, self._not_nullable),
            )

    def _type_check(self, value: Any) -> None:
        type_ = self._type
        if type_ is Any:
            return
        if not isinstance(value, type_):
            raise ValidationError(
                Constraint("type", (type_, type(value)), locale["type"])
            )

    def transform(self, func: TransformFunc) -> 'Schema':
        self._transforms: List[TransformFunc]
        self._transforms.append(func)
        return self

    def test(self, func: ValidatorFunc) -> 'Schema':
        self._validators: List[ValidatorFunc]
        self._validators.append(func)
        return self

    def validate(self, value: _T, abort_early: bool = True, path: str = "") -> _T:
        try:
            if value is None:
                self._nullable_check()
                return value

            self._type_check(value)

            transformed: _T = value
            for t in self._transforms:
                transformed = t(transformed)

            for v in self._validators:
                v(transformed)
            return transformed
        except ValidationError as err:
            raise ValidationError(err.constraint, path)
