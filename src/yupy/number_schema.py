from dataclasses import dataclass, field
from typing import Union, TypeAlias, TypeVar

from typing_extensions import Self

from yupy.icomparable_schema import ComparableSchema
from yupy.ischema import _SchemaExpectedType
from yupy.locale import locale
from yupy.validation_error import ErrorMessage, ValidationError, Constraint

__all__ = ('NumberSchema',)

_T = TypeVar('_T')
_NumberType: TypeAlias = Union[int, float]


@dataclass
class NumberSchema(ComparableSchema[_T]):
    _type: _SchemaExpectedType = field(init=False, default=(float, int))

    def positive(self, message: ErrorMessage = locale["positive"]) -> Self:
        return self.gt(0, message)

    def negative(self, message: ErrorMessage = locale["negative"]) -> Self:
        return self.lt(0, message)

    def integer(self, message: ErrorMessage = locale["integer"]) -> Self:
        def _(x: _NumberType) -> None:
            if (x % 1) != 0:
                raise ValidationError(Constraint("integer", message), invalid_value=x)

        return self.test(_)

    # def truncate(self):
    #     ...

    # def round(self, method: Literal['ceil', 'floor', 'round', 'trunc']) -> 'NumberSchema':
    #     self._transforms

    def multiple_of(self, multiplier: Union[int, float],
                    message: ErrorMessage = locale["multiple_of"]) -> Self:
        def _(x: Union[int, float]) -> None:
            if x % multiplier != 0:
                raise ValidationError(Constraint("multiple_of", message, multiplier), invalid_value=x)

        return self.test(_)
