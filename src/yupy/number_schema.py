from dataclasses import dataclass, field
from typing import Union, TypeAlias, TypeVar

from typing_extensions import Self

from yupy.icomparable_schema import ComparableSchema, EqualityComparableSchema
from yupy.ischema import _SchemaExpectedType
from yupy.locale import locale, ErrorMessage
from yupy.validation_error import ValidationError, Constraint

__all__ = ('NumberSchema',)

_T = TypeVar('_T')
_NumberType: TypeAlias = Union[int, float]


@dataclass
class NumberSchema(ComparableSchema, EqualityComparableSchema):
    """
    A schema for validating numerical values (integers and floats).

    This schema provides methods for enforcing positivity, negativity,
    integer-only values, and divisibility by a multiplier.

    Inherits from `ComparableSchema` for comparison operations (le, ge, lt, gt)
    and `EqualityComparableSchema` for equality operations (eq, ne).

    Attributes:
        _type (_SchemaExpectedType): The expected Python type(s) for the schema's value.
            Initialized to `(float, int)` to allow both float and integer types.
    """
    _type: _SchemaExpectedType = field(init=False, default=(float, int))

    def positive(self, message: ErrorMessage = locale["positive"]) -> Self:
        """
        Adds a validation rule to ensure the number is positive (greater than 0).

        This method internally uses `gt(0)`.

        Args:
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "positive".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """
        return self.gt(0, message)

    def negative(self, message: ErrorMessage = locale["negative"]) -> Self:
        """
        Adds a validation rule to ensure the number is negative (less than 0).

        This method internally uses `lt(0)`.

        Args:
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "negative".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """
        return self.lt(0, message)

    def integer(self, message: ErrorMessage = locale["integer"]) -> Self:
        """
        Adds a validation rule to ensure the number is an integer (has no decimal part).

        Args:
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "integer".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

        def _(x: _NumberType) -> None:
            if (x % 1) != 0:
                raise ValidationError(Constraint("integer", message), invalid_value=x)

        return self.test(_)

    # TODO:
    # def truncate(self):
    #     ...

    # TODO:
    # def round(self, method: Literal['ceil', 'floor', 'round', 'trunc']) -> 'NumberSchema':
    #     self._transforms

    def multiple_of(self, multiplier: Union[int, float],
                    message: ErrorMessage = locale["multiple_of"]) -> Self:
        """
        Adds a validation rule to ensure the number is a multiple of a given multiplier.

        Args:
            multiplier (Union[int, float]): The number that the validated value
                must be a multiple of.
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "multiple_of".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

        def _(x: Union[int, float]) -> None:
            if x % multiplier != 0:
                raise ValidationError(Constraint("multiple_of", message, multiplier), invalid_value=x)

        return self.test(_)
