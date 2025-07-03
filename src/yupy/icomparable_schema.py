from typing import Protocol, Any, runtime_checkable

from typing_extensions import Self

from yupy.locale import ErrorMessage
from yupy.locale import locale
from yupy.schema import Schema
from yupy.validation_error import ValidationError, Constraint

__all__ = (
    'IEqualityComparableSchema',
    'IComparableSchema',
    'EqualityComparableSchema',
    'ComparableSchema',
)


@runtime_checkable
class IEqualityComparableSchema(Protocol):
    """
    IEqualityComparableSchema defines the interface for schemas that support
    equality and inequality comparisons.
    """

    def eq(self, value: Any, message: ErrorMessage = locale["eq"]) -> Self:
        """
        Adds a validation rule to ensure the value is strictly equal to a given value.

        Args:
            value (Any): The value to compare against.
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "eq".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

    def ne(self, value: Any, message: ErrorMessage = locale["ne"]) -> Self:
        """
        Adds a validation rule to ensure the value is not equal to a given value.

        Args:
            value (Any): The value to compare against.
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "ne".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """


@runtime_checkable
class IComparableSchema(Protocol):
    """
    IComparableSchema defines the interface for schemas that support
    various comparison operations (less than, greater than, etc.).
    """

    def le(self, limit: Any, message: ErrorMessage = locale["le"]) -> Self:
        """
        Adds a validation rule to ensure the value is less than or equal to a limit.

        Args:
            limit (Any): The upper limit for the value.
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "le".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

    def ge(self, limit: Any, message: ErrorMessage = locale["ge"]) -> Self:
        """
        Adds a validation rule to ensure the value is greater than or equal to a limit.

        Args:
            limit (Any): The lower limit for the value.
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "ge".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

    def lt(self, limit: Any, message: ErrorMessage = locale["lt"]) -> Self:
        """
        Adds a validation rule to ensure the value is strictly less than a limit.

        Args:
            limit (Any): The upper limit for the value (exclusive).
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "lt".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

    def gt(self, limit: Any, message: ErrorMessage = locale["gt"]) -> Self:
        """
        Adds a validation rule to ensure the value is strictly greater than a limit.

        Args:
            limit (Any): The lower limit for the value (exclusive).
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "gt".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """


class EqualityComparableSchema(Schema):
    """
    A base schema class that provides methods for equality and inequality comparisons.

    Inherits from `Schema` and implements `IEqualityComparableSchema`.
    """

    def eq(self, value: Any, message: ErrorMessage = locale["eq"]) -> Self:
        """
        Adds a validation rule to ensure the value is strictly equal to a given value.

        Args:
            value (Any): The value to compare against.
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "eq".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

        def _(x: Any) -> None:
            if x != value:
                raise ValidationError(Constraint("eq", message, value), invalid_value=x)

        return self.test(_)

    def ne(self, value: Any, message: ErrorMessage = locale["ne"]) -> Self:
        """
        Adds a validation rule to ensure the value is not equal to a given value.

        Args:
            value (Any): The value to compare against.
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "ne".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

        def _(x: Any) -> None:
            if x == value:
                raise ValidationError(Constraint("ne", message, value), invalid_value=x)

        return self.test(_)


class ComparableSchema(Schema):
    """
    A base schema class that provides methods for various comparison operations.

    Inherits from `Schema` and implements `IComparableSchema`.
    """

    def le(self, limit: Any, message: ErrorMessage = locale["le"]) -> Self:
        """
        Adds a validation rule to ensure the value is less than or equal to a limit.

        Args:
            limit (Any): The upper limit for the value.
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "le".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

        def _(x: Any) -> None:
            if x > limit:
                raise ValidationError(Constraint("le", message, limit), invalid_value=x)

        return self.test(_)

    def ge(self, limit: Any, message: ErrorMessage = locale["ge"]) -> Self:
        """
        Adds a validation rule to ensure the value is greater than or equal to a limit.

        Args:
            limit (Any): The lower limit for the value.
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "ge".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

        def _(x: Any) -> None:
            if x < limit:
                raise ValidationError(Constraint("ge", message, limit), invalid_value=x)

        return self.test(_)

    def lt(self, limit: Any, message: ErrorMessage = locale["lt"]) -> Self:
        """
        Adds a validation rule to ensure the value is strictly less than a limit.

        Args:
            limit (Any): The upper limit for the value (exclusive).
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "lt".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

        def _(x: Any) -> None:
            if x >= limit:
                raise ValidationError(Constraint("lt", message, limit), invalid_value=x)

        return self.test(_)

    def gt(self, limit: Any, message: ErrorMessage = locale["gt"]) -> Self:
        """
        Adds a validation rule to ensure the value is strictly greater than a limit.

        Args:
            limit (Any): The lower limit for the value (exclusive).
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "gt".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

        def _(x: Any) -> None:
            if x <= limit:
                raise ValidationError(Constraint("gt", message, limit), invalid_value=x)

        return self.test(_)
