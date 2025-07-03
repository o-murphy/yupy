import re
from dataclasses import field, dataclass

from typing_extensions import Self

from yupy.icomparable_schema import ComparableSchema, EqualityComparableSchema
from yupy.ischema import _SchemaExpectedType
from yupy.isized_schema import SizedSchema
from yupy.locale import locale, ErrorMessage
from yupy.validation_error import ValidationError, Constraint

__all__ = ('StringSchema',)

rUUID_pattern = re.compile(
    r"^(?:[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}|00000000-0000-0000-0000-000000000000)$",
    re.IGNORECASE,
)
"""
Regular expression pattern for validating UUIDs (versions 1-5) and the null UUID.
The validation is case-insensitive.
"""

rEmail_pattern = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$",
    re.IGNORECASE,
)
"""
Regular expression pattern for validating email addresses.
The validation is case-insensitive.
"""

rUrl_pattern = re.compile(
    r"^((https?|ftp):)?//(((([a-z]|\d|-|\.|_|~|[ -퟿豈-﷏ﷰ-￯])|(%[\da-f]{2})|[!$&'()*+,;=]|:)*@)?(((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|((([a-z]|\d|[ -퟿豈-﷏ﷰ-￯])|(([a-z]|\d|[ -퟿豈-﷏ﷰ-￯])([a-z]|\d|-|\.|_|~|[ -퟿豈-﷏ﷰ-￯])*([a-z]|\d|[ -퟿豈-﷏ﷰ-￯])))\.)+(([a-z]|[ -퟿豈-﷏ﷰ-￯])|(([a-z]|[ -퟿豈-﷏ﷰ-￯])([a-z]|\d|-|\.|_|~|[ -퟿豈-﷏ﷰ-￯])*([a-z]|[ -퟿豈-﷏ﷰ-￯])))\.?)(:\d*)?)(/((([a-z]|\d|-|\.|_|~|[ -퟿豈-﷏ﷰ-￯])|(%[\da-f]{2})|[!$&'()*+,;=]|:|@)+(/(([a-z]|\d|-|\.|_|~|[ -퟿豈-﷏ﷰ-￯])|(%[\da-f]{2})|[!$&'()*+,;=]|:|@)*)*)?)?(\?((([a-z]|\d|-|\.|_|~|[ -퟿豈-﷏ﷰ-￯])|(%[\da-f]{2})|[!$&'()*+,;=]|:|@)|[-]|/|\?)*)?(#((([a-z]|\d|-|\.|_|~|[ -퟿豈-﷏ﷰ-￯])|(%[\da-f]{2})|[!$&'()*+,;=]|:|@)|/|\?)*)?$",
    re.IGNORECASE,
)
"""
Regular expression pattern for validating URLs.
The validation is case-insensitive.
"""


@dataclass
class StringSchema(SizedSchema, ComparableSchema, EqualityComparableSchema):
    """
    A schema for validating string values with various constraints.

    This schema extends `SizedSchema` for length-based validations,
    `ComparableSchema` for comparison operations, and
    `EqualityComparableSchema` for equality checks. It provides methods
    for regex matching, specific format validation (email, URL, UUID),
    case enforcement, and ensuring non-empty strings.

    Attributes:
        _type (_SchemaExpectedType): The expected Python type for the schema's value.
            Initialized to `str`.
    """
    _type: _SchemaExpectedType = field(init=False, default=str)

    def matches(self, regex: re.Pattern, message: ErrorMessage = locale["matches"],
                exclude_empty: bool = False) -> Self:
        """
        Adds a validation rule to ensure the string matches a given regular expression pattern.

        Args:
            regex (re.Pattern): The compiled regular expression pattern to match.
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "matches".
            exclude_empty (bool): If True, an empty string will not trigger this
                validation rule and will be considered valid for this specific check.
                Defaults to False.

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

        def _(x: str) -> None:
            if exclude_empty and not x:
                return

            if not re.match(regex, x):
                raise ValidationError(Constraint("matches", message, regex.pattern), invalid_value=x)

        return self.test(_)

    def email(self, message: ErrorMessage = locale["email"]) -> Self:
        """
        Adds a validation rule to ensure the string is a valid email address format.

        This method uses the pre-compiled `rEmail_pattern` for validation.

        Args:
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "email".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

        def _(x: str) -> None:
            if not re.match(rEmail_pattern, x):
                raise ValidationError(Constraint("email", message), invalid_value=x)

        return self.test(_)

    def url(self, message: ErrorMessage = locale["url"]) -> Self:
        """
        Adds a validation rule to ensure the string is a valid URL format.

        This method uses the pre-compiled `rUrl_pattern` for validation.

        Args:
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "url".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

        def _(x: str) -> None:
            if not re.match(rUrl_pattern, x):
                raise ValidationError(Constraint("url", message), invalid_value=x)

        return self.test(_)

    def uuid(self, message: ErrorMessage = locale["uuid"]) -> Self:
        """
        Adds a validation rule to ensure the string is a valid UUID format.

        This method uses the pre-compiled `rUUID_pattern` for validation,
        which includes support for UUID versions 1-5 and the null UUID.

        Args:
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "uuid".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

        def _(x: str) -> None:
            if not re.match(rUUID_pattern, x):
                raise ValidationError(Constraint("uuid", message), invalid_value=x)

        return self.test(_)

    # TODO:
    # def datetime(self, message: ErrorMessage, precision: int, allow_offset: bool = False):
    #     def _(x: str):
    #         if ...:
    #             raise ValidationError(message)
    #     self._validators.append(_)
    #     return self

    def ensure(self) -> Self:
        """
        Adds a transformation to ensure that if the string value is falsy (e.g., empty string),
        it is transformed into an empty string `""`.

        This is useful for normalizing values where `None` or other falsy values
        should be treated as an empty string.

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

        def _(x: str) -> str:
            return x if x else ""

        self._transforms.append(_)
        return self

    # TODO:
    # def trim(self, message: ErrorMessage):
    #     ...

    def lowercase(self, message: ErrorMessage = locale["lowercase"]) -> Self:
        """
        Adds a validation rule to ensure the string contains only lowercase characters.

        The validation checks if the string is identical to its lowercase version.

        Args:
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "lowercase".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

        def _(x: str) -> None:
            if x.lower() != x:
                raise ValidationError(Constraint("lowercase", message), invalid_value=x)

        return self.test(_)

    def uppercase(self, message: ErrorMessage = locale["uppercase"]) -> Self:
        """
        Adds a validation rule to ensure the string contains only uppercase characters.

        The validation checks if the string is identical to its uppercase version.

        Args:
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "uppercase".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

        def _(x: str) -> None:
            if x.upper() != x:
                raise ValidationError(Constraint("uppercase", message), invalid_value=x)

        return self.test(_)
