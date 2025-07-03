from typing import Optional, Literal, TypedDict, TypeAlias, Union, Callable, Any, List

__all__ = (
    'locale',
    'set_locale',
    'get_error_message',
    'ErrorMessage',
)

ErrorMessage: TypeAlias = Union[str, Callable[[Any | List[Any]], str]]
"""
Type alias for an error message.

Can be a simple string or a callable that takes arguments (e.g., validation
limits, invalid values) and returns a formatted string.
"""


class Locale(TypedDict, total=False):
    """
    A TypedDict representing the structure of the locale dictionary.

    Each key corresponds to a specific validation error type, and its value
    is an `ErrorMessage` (either a string or a callable).
    `total=False` indicates that not all keys are required to be present
    when creating a `Locale` instance.
    """
    const: ErrorMessage
    type: ErrorMessage
    min: ErrorMessage
    max: ErrorMessage
    length: ErrorMessage
    required: ErrorMessage
    nullable: ErrorMessage
    not_nullable: ErrorMessage
    test: ErrorMessage
    matches: ErrorMessage
    email: ErrorMessage
    url: ErrorMessage
    uuid: ErrorMessage
    lowercase: ErrorMessage
    uppercase: ErrorMessage
    le: ErrorMessage
    ge: ErrorMessage
    lt: ErrorMessage
    gt: ErrorMessage
    eq: ErrorMessage
    ne: ErrorMessage
    integer: ErrorMessage
    multiple_of: ErrorMessage
    positive: ErrorMessage
    negative: ErrorMessage
    date: ErrorMessage
    datetime: ErrorMessage
    array: ErrorMessage
    mapping: ErrorMessage
    strict: ErrorMessage
    one_of: ErrorMessage
    json: ErrorMessage
    undefined: ErrorMessage


LocaleKey = Literal[
    "const", "type", "min", "max", "length", "required", "nullable", "not_nullable", "test", "matches",
    "email", "url", "uuid", "lowercase", "uppercase",
    "le", "ge", "lt", "gt", "eq", "ne",
    "integer", "multiple_of", "positive", "negative", "date", "datetime",
    "array", "mapping", "strict", "one_of", "json", "undefined"
]
"""
Literal type defining all valid keys for the `locale` dictionary.
"""

locale: Locale = {
    "const": lambda args: "Value is not match the const %r" % args,
    "type": lambda args: "Value is not of type %r, got %r" % args,
    "min": lambda args: "Min length must be %r" % args,
    "max": lambda args: "Max length must be %r" % args,
    "length": lambda args: "Length must be %r" % args,
    "uppercase": "Value must be an uppercase string",
    "lowercase": "Value must be a lowercase string",
    "required": "Value is required",
    "nullable": "Value can't be null",
    "not_nullable": "Value can't be null",
    "test": "Test failed",
    'matches': "Don't match regex",  # FIXME
    "email": "Value must be a valid email",
    "url": "Value must be a valid URL",
    "uuid": "Value must be a valid UUID",
    "le": lambda args: "Value must be less or equal to %r" % args,
    "ge": lambda args: "Value must be greater or equal to %r" % args,
    "lt": lambda args: "Value must be less than %r" % args,
    "gt": lambda args: "Value must be greater than %r" % args,
    "eq": lambda args: "Value must be equal to %r" % args,
    "ne": lambda args: "Value must be not equal to %r" % args,
    "positive": "Value must be positive, a.g. > 0",
    "negative": "Value must be positive, a.g. < 0",
    "integer": "Value must be valid 'int', got 'float'",
    "date": "Value must be a valid ISO 8601 date (YYYY-MM-DD)",
    "datetime": "Value must be a valid ISO 8601 datetime",
    "array": "Invalid array",
    "mapping": "Invalid mapping",
    "multiple_of": lambda args: "Value must be a multiple of %r" % args,
    "strict": lambda args: "Object contains unknown keys: %s" % (", ".join(map(repr, args)),),
    "one_of": lambda args: "Must be one of %r" % args,
    "json": lambda args: "Value must be a valid JSON",
    "undefined": "Undefined validation error"
}
"""
The default locale dictionary containing various error messages.

These messages are used by schemas when validation fails. Some messages are
callable lambdas that allow for dynamic message formatting based on validation
arguments.
"""


def set_locale(locale_: Optional[Locale] = None) -> Locale:
    """
    Sets or updates the global locale dictionary with custom error messages.

    If a `locale_` dictionary is provided, its key-value pairs will update
    the existing `locale` dictionary. If `None` is provided, the current
    `locale` dictionary is returned without modification.

    Args:
        locale_ (Optional[Locale]): A dictionary of locale messages to set or update.
            If None, the current locale is returned.

    Returns:
        Locale: The updated (or current) global locale dictionary.
    """
    if locale_:
        locale.update(locale_)
    return locale


def get_error_message(key: LocaleKey) -> ErrorMessage:
    """
    Retrieves an error message from the current locale dictionary by its key.

    If the key is not found, a generic "undefined" error message is returned.

    Args:
        key (LocaleKey): The key corresponding to the desired error message.

    Returns:
        ErrorMessage: The error message (string or callable) associated with the key.
    """
    return locale.get(key, "undefined")
