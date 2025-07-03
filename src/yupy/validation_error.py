from dataclasses import dataclass, field
from typing import Generator, Any, List, Optional, Union

from yupy.locale import get_error_message, ErrorMessage

__all__ = (
    'ValidationError',
    'Constraint',
    '_EMPTY_MESSAGE_',
)

_EMPTY_MESSAGE_: ErrorMessage = ""
"""
A sentinel value for an empty error message, used to indicate that the default
message from the locale should be used.
"""


@dataclass
class Constraint:
    """
    Represents a single validation constraint that was violated.

    This class holds information about the type of constraint (e.g., "type", "min"),
    any arguments associated with the constraint (e.g., the minimum length),
    and the specific error message for this violation.

    Attributes:
        type (str): The type of the constraint (e.g., "required", "length").
        args (Any): Arguments associated with the constraint, used for formatting
            the error message (e.g., the expected type, the limit for length).
        message (ErrorMessage): The raw error message template or string.
            This field is excluded from `repr()` to avoid verbosity.
        origin: Optional[Exception]: wrapped exception.
    """
    type: Optional[str]
    args: Any
    message: ErrorMessage = field(repr=False)
    origin: Optional[Exception]

    def __init__(self,
                 type_: Optional[str] = "unknown",
                 message: Optional[ErrorMessage] = _EMPTY_MESSAGE_,
                 *args: Any,
                 origin: Optional[Exception] = None,
                 ):
        """
        Initializes a new Constraint instance.

        Args:
            type_ (Optional[str]): The type of the constraint (e.g., "required").
                Defaults to "undefined" if None.
            message (Optional[ErrorMessage], optional): The specific error message
                for this constraint. If `None` or `_EMPTY_MESSAGE_`, the default
                "undefined" message from the locale will be used. Defaults to `_EMPTY_MESSAGE_`.
            *args (Any): Positional arguments that will be passed to the message
                formatter if the message is a callable.
        """
        self.type = type_ or "undefined"
        self.args = args
        self.origin = origin
        if message is None or message is _EMPTY_MESSAGE_:  # Check against _EMPTY_MESSAGE_ for default behavior
            self.message = get_error_message("undefined")
        else:
            self.message = message

    @property
    def format_message(self) -> str:
        """
        Formats the error message using the constraint's arguments.

        If the `message` is a callable (e.g., a lambda function), it's invoked
        with `self.args` to produce the final string. Otherwise, the `message`
        string itself is returned.

        Returns:
            str: The formatted error message.
        """
        if callable(self.message):
            return self.message(self.args)
        return self.message


class ValidationError(ValueError):
    """
    Represents a validation error, potentially containing nested errors.

    This exception is raised when a schema validation fails. It can encapsulate
    a single constraint violation or a collection of multiple violations
    (e.g., when `abort_early` is False in schema validation).

    Attributes:
        constraint (Constraint): The primary constraint that was violated for
            this specific error.
        path (str): The path within the validated data structure where the error occurred.
        _errors (List[ValidationError]): A private list of nested `ValidationError`
            instances, used when collecting multiple errors (e.g., for object or array schemas).
        invalid_value (Optional[Any]): The value that failed validation.
    """

    def __init__(
            self, constraint: Optional[Constraint] = None, path: str = "",
            errors: Optional[List['ValidationError']] = None,
            invalid_value: Optional[Any] = None, *args) -> None:
        """
        Initializes a new ValidationError instance.

        Args:
            constraint (Optional[Constraint], optional): The primary constraint
                that was violated. If None, a default "undefined" constraint is created.
                Defaults to None.
            path (str, optional): The path within the data structure where the
                error occurred. Defaults to "".
            errors (Optional[List['ValidationError']], optional): A list of nested
                `ValidationError` instances, used for collecting multiple errors.
                Defaults to None.
            invalid_value (Optional[Any], optional): The value that caused the validation
                failure. Defaults to None.
            *args: Additional arguments passed to the base `ValueError` constructor.
        """
        if not constraint:
            self.constraint = Constraint("undefined")
        else:
            self.constraint = constraint
        self.path = path
        self._errors: List[ValidationError] = errors or []
        self.invalid_value: Optional[Any] = invalid_value
        # The base ValueError constructor expects a single string or tuple of args
        # We pass self.path, self.constraint, self._errors as arguments to ValueError
        super().__init__(self.path, self.constraint, self._errors, *args)

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the validation error.

        Returns:
            str: A string in the format "(path='...', constraint=Constraint(...), message='...')".
        """
        return "(path=%r, constraint=%r, message=%r)" % (self.path, self.constraint, self.constraint.format_message)

    def __repr__(self) -> str:
        """
        Returns the official string representation of the ValidationError object.

        Returns:
            str: A string in the format "ValidationError(path='...', constraint=Constraint(...), message='...')".
        """
        return "ValidationError%s" % self.__str__()

    @property
    def errors(self) -> Generator['ValidationError', None, None]:
        """
        A generator that yields this validation error and all its nested errors recursively.

        This allows for easy iteration over all individual validation failures
        within a complex data structure.

        Yields:
            ValidationError: The current error instance, then all its sub-errors.
        """
        yield self
        for error in self._errors:
            yield from error.errors

    @property
    def message(self) -> str:
        """
        Returns a concise message for this specific validation error, including its path.

        Returns:
            str: A string in the format "'path':'formatted_constraint_message'".
        """
        return "%r:%s" % (self.path, self.constraint.format_message)

    @property
    def messages(self) -> Generator[Union[property, str], None, None]:
        """
        A generator that yields the concise message for this validation error
        and all its nested errors recursively.

        Yields:
            str: The formatted message for the current error, then for all its sub-errors.
        """
        for e in self.errors:
            yield e.message
