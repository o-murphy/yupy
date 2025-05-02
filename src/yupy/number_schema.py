from dataclasses import dataclass, field
from typing import Union, TypeAlias

from yupy.locale import locale
from yupy.ischema import _SchemaExpectedType
from yupy.schema import Schema
from yupy.validation_error import ErrorMessage, ValidationError, Constraint

__all__ = ('NumberSchema',)

_NumberType: TypeAlias = Union[int, float]

@dataclass
class NumberSchema(Schema[_NumberType]):
    _type: _SchemaExpectedType = field(init=False, default=(float, int))

    def le(self, limit: _NumberType, message: ErrorMessage = locale["le"]) -> 'Schema[_NumberType]':
        def _(x: _NumberType) -> None:
            if x > limit:
                raise ValidationError(Constraint("le", limit, message))

        return self.test(_)

    def ge(self, limit: _NumberType, message: ErrorMessage = locale["ge"]) -> 'Schema[_NumberType]':
        def _(x: _NumberType) -> None:
            if x < limit:
                raise ValidationError(Constraint("ge", limit, message))

        return self.test(_)

    def lt(self, limit: _NumberType, message: ErrorMessage = locale["lt"]) -> 'Schema[_NumberType]':
        def _(x: _NumberType) -> None:
            if x >= limit:
                raise ValidationError(Constraint("lt", limit, message))

        return self.test(_)

    def gt(self, limit: _NumberType, message: ErrorMessage = locale["gt"]) -> 'Schema[_NumberType]':
        def _(x: _NumberType) -> None:
            if x <= limit:
                raise ValidationError(Constraint("gt", limit, message))

        return self.test(_)

    def positive(self, message: ErrorMessage = locale["positive"]) -> 'Schema[_NumberType]':
        return self.gt(0, message)

    def negative(self, message: ErrorMessage = locale["negative"]) -> 'Schema[_NumberType]':
        return self.lt(0, message)

    def integer(self, message: ErrorMessage = locale["integer"]) -> 'Schema[_NumberType]':
        def _(x: _NumberType) -> None:
            if (x % 1) != 0:
                raise ValidationError(Constraint("integer", None, message))

        return self.test(_)

    # def truncate(self):
    #     ...

    # def round(self, method: Literal['ceil', 'floor', 'round', 'trunc']) -> 'NumberSchema':
    #     self._transforms

    def multiple_of(self, multiplier: Union[int, float],
                    message: ErrorMessage = locale["multiple_of"]) -> 'Schema[_NumberType]':
        def _(x: Union[int, float]) -> None:
            if x % multiplier != 0:
                raise ValidationError(Constraint("multiple_of", multiplier, message))

        return self.test(_)
