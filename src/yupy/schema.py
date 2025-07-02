from dataclasses import field, dataclass
from typing import Any, List, Optional

from typing_extensions import Self

from yupy.ischema import TransformFunc, ValidatorFunc, _SchemaExpectedType
from yupy.locale import locale
from yupy.validation_error import ErrorMessage, ValidationError, Constraint

__all__ = ('Schema',)


@dataclass
class Schema:  # Implement ISchema
    _type: _SchemaExpectedType = field(default=object)
    _transforms: List[TransformFunc] = field(init=False, default_factory=list)
    _validators: List[ValidatorFunc] = field(init=False, default_factory=list)
    _nullability: bool = False
    _not_nullable: ErrorMessage = locale["not_nullable"]

    @property
    def nullability(self) -> bool:
        return self._nullability

    def nullable(self) -> Self:
        self._nullability: bool = True
        return self

    def not_nullable(self, message: ErrorMessage = locale["not_nullable"]) -> Self:
        self._nullability: bool = False
        self._not_nullable: ErrorMessage = message
        return self

    def _nullable_check(self, value: Any) -> None:
        if not self._nullability and value is None:
            raise ValidationError(
                Constraint("nullable", self._not_nullable),
                invalid_value=value
            )

    def _type_check(self, value: Any) -> None:
        type_ = self._type
        if type_ is Any:
            return
        if not isinstance(value, type_):
            raise ValidationError(
                Constraint("type", locale["type"], type_, type(value)),
                invalid_value=value
            )

    def transform(self, func: TransformFunc) -> Self:
        self._transforms: List[TransformFunc]
        self._transforms.append(func)
        return self

    def _transform(self, value: Any) -> Any:
        transformed: Any = value
        for t in self._transforms:
            transformed = t(transformed)
        return transformed

    def test(self, func: ValidatorFunc) -> Self:
        self._validators.append(func)
        return self

    def validate(self, value: Any = None, abort_early: bool = True, path: str = "~") -> Any:
        try:
            self._nullable_check(value)
            transformed = self._transform(value)
            self._type_check(transformed)

            for v in self._validators:
                v(transformed)
            return transformed
        except ValidationError as err:
            raise ValidationError(err.constraint, path, invalid_value=value)

    def const(self, value: Optional[_SchemaExpectedType], message: ErrorMessage = locale["const"]) -> Self:
        def _(x: Any) -> None:
            if x != value:
                raise ValidationError(Constraint("const", message, value), invalid_value=x)

        return self.test(_)