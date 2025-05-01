from dataclasses import dataclass, field
from typing import Union, Type, Tuple

from yupy.locale import locale
from yupy.schema import Schema
from yupy.validation_error import ErrorMessage, ValidationError, Constraint

__all__ = ('NumberSchema',)


@dataclass
class NumberSchema(Schema[Union[int, float]]):
    _type: Type[Tuple[Type[float], Type[int]]] = field(init=False, default=(float, int))

    def le(self, limit: Union[int, float], message: ErrorMessage = locale["le"]) -> 'Self':
        def _(x: Union[int, float]) -> None:
            if x > limit:
                raise ValidationError(Constraint("le", limit, message))

        return self.test(_)

    def ge(self, limit: Union[int, float], message: ErrorMessage = locale["ge"]) -> 'Self':
        def _(x: Union[int, float]) -> None:
            if x < limit:
                raise ValidationError(Constraint("ge", limit, message))

        return self.test(_)

    def lt(self, limit: Union[int, float], message: ErrorMessage = locale["lt"]) -> 'Self':
        def _(x: Union[int, float]) -> None:
            if x >= limit:
                raise ValidationError(Constraint("lt", limit, message))

        return self.test(_)

    def gt(self, limit: Union[int, float], message: ErrorMessage = locale["gt"]) -> 'Self':
        def _(x: Union[int, float]) -> None:
            if x <= limit:
                raise ValidationError(Constraint("gt", limit, message))

        return self.test(_)

    def positive(self, message: ErrorMessage = locale["positive"]) -> 'Self':
        return self.gt(0, message)

    def negative(self, message: ErrorMessage = locale["negative"]) -> 'Self':
        return self.lt(0, message)

    def integer(self, message: ErrorMessage = locale["integer"]) -> 'Self':
        def _(x: Union[int, float]) -> None:
            if (x % 1) != 0:
                raise ValidationError(Constraint("integer", None, message))

        return self.test(_)

    # def truncate(self):
    #     ...

    # def round(self, method: Literal['ceil', 'floor', 'round', 'trunc']) -> 'Self':
    #     self._transforms

    def multiple_of(self, multiplier: Union[int, float],
                    message: ErrorMessage = locale["multiple_of"]) -> 'Self':
        def _(x: Union[int, float]) -> None:
            if x % multiplier != 0:
                raise ValidationError(Constraint("multiple_of", multiplier, message))

        return self.test(_)
