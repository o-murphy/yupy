from dataclasses import dataclass
from typing import Sized, Protocol, runtime_checkable

from typing_extensions import Self

from yupy.locale import ErrorMessage
from yupy.locale import locale
from yupy.schema import Schema
from yupy.validation_error import ValidationError, Constraint

__all__ = ('ISizedSchema', 'SizedSchema')


@runtime_checkable
class ISizedSchema(Protocol):
    """
    ISizedSchema defines the interface for schemas that can validate
    the size or length of a value (e.g., strings, lists, tuples).
    """

    def length(self, limit: int, message: ErrorMessage = locale["length"]) -> Self:
        """
        Adds a validation rule to ensure the value has an exact length.

        Args:
            limit (int): The required length of the value.
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "length".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

    def min(self, limit: int, message: ErrorMessage = locale["min"]) -> Self:
        """
        Adds a validation rule to ensure the value has a minimum length.

        Args:
            limit (int): The minimum required length of the value.
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "min".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

    def max(self, limit: int, message: ErrorMessage = locale["max"]) -> Self:
        """
        Adds a validation rule to ensure the value has a maximum length.

        Args:
            limit (int): The maximum allowed length of the value.
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "max".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """


@dataclass
class SizedSchema(Schema):
    """
    A schema class that provides methods for validating the size or length of a value.

    This schema is designed to work with objects that implement the `Sized` protocol,
    meaning they have a `__len__` method (e.g., strings, lists, dictionaries, tuples).

    Inherits from `Schema` and implements `ISizedSchema`.
    """

    def length(self, limit: int, message: ErrorMessage = locale["length"]) -> Self:
        """
        Adds a validation rule to ensure the value has an exact length.

        Args:
            limit (int): The required length of the value.
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "length".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

        def _(x: Sized) -> None:  # Use Sized instead of Iterable
            if len(x) != limit:
                raise ValidationError(Constraint("length", message, limit), invalid_value=x)

        return self.test(_)

    def min(self, limit: int, message: ErrorMessage = locale["min"]) -> Self:
        """
        Adds a validation rule to ensure the value has a minimum length.

        Args:
            limit (int): The minimum required length of the value.
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "min".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

        def _(x: Sized) -> None:  # Use Sized instead of Iterable
            if len(x) < limit:
                raise ValidationError(Constraint("min", message, limit), invalid_value=x)

        return self.test(_)

    def max(self, limit: int, message: ErrorMessage = locale["max"]) -> Self:
        """
        Adds a validation rule to ensure the value has a maximum length.

        Args:
            limit (int): The maximum allowed length of the value.
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "max".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

        def _(x: Sized) -> None:  # Use Sized instead of Iterable
            if len(x) > limit:
                raise ValidationError(Constraint("max", message, limit), invalid_value=x)

        return self.test(_)
