from dataclasses import dataclass, field
from typing import Any, Iterable

from typing_extensions import Self

from yupy.icomparable_schema import EqualityComparableSchema
from yupy.ischema import _SchemaExpectedType
from yupy.locale import locale, ErrorMessage
from yupy.validation_error import Constraint, ValidationError

__all__ = ('MixedSchema',)


@dataclass
class MixedSchema(EqualityComparableSchema):
    """
    A schema for validating mixed types, offering flexible type checking
    and enumeration validation.

    Inherits from `EqualityComparableSchema` to provide equality comparison methods.

    Attributes:
        _type (_SchemaExpectedType): The expected Python type(s) for the schema's value.
            Defaults to `object`, meaning any type is initially allowed.
    """
    _type: _SchemaExpectedType = field(default=object)

    def of(self, type_: _SchemaExpectedType, message: ErrorMessage = locale["type"]) -> Self:
        """
        Adds a validation rule to ensure the value is of a specific type or types.

        If `type_` is `Any`, no type check is performed.

        Args:
            type_ (_SchemaExpectedType): The expected Python type(s) for the value.
                Can be a single type (e.g., `str`), a UnionType (e.g., `str | int`),
                or a tuple of types (e.g., `(str, int)`).
            message (ErrorMessage): The error message to use if the type validation fails.
                Defaults to the locale-defined message for "type".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

        def _(x: Any) -> None:
            if type_ is Any:
                return
            if not isinstance(x, type_):
                raise ValidationError(
                    Constraint("type", message, type_, type(x)),
                    invalid_value=x
                )

        return self.test(_)

    def one_of(self, items: Iterable, message: ErrorMessage = locale['one_of']) -> Self:
        """
        Adds a validation rule to check if the value is one of the provided items.

        Args:
            items (Iterable): An iterable (e.g., list, tuple, set) containing
                the allowed values.
            message (ErrorMessage): The error message to use if the value is not
                found in the `items`. Defaults to the locale-defined message for "one_of".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

        def _(x: Any) -> None:
            if x not in items:
                raise ValidationError(Constraint('one_of', message, items), invalid_value=x)

        return self.test(_)
